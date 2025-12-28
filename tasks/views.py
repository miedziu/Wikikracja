import math

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DetailView, TemplateView, UpdateView

from .forms import TaskForm, TaskStatusForm
from .models import Task, TaskEvaluation, TaskVote


PRIORITY_LABELS = {
    "critical": _("Critical"),
    "important": _("Important"),
    "beneficial": _("Beneficial"),
    "rejected": _("Rejected"),
}


def _assign_priorities(tasks):
    for task in tasks:
        task.priority_label = None
        task.priority_category = None

    non_negative = [t for t in tasks if (t.votes_score or 0) >= 0]
    negative = [t for t in tasks if (t.votes_score or 0) < 0]
    total = len(non_negative)

    def mark(task, category):
        task.priority_category = category
        task.priority_label = PRIORITY_LABELS[category]

    if total == 0:
        for task in negative:
            mark(task, "rejected")
        return

    critical_limit = max(1, math.ceil(total * 0.2))
    important_limit = critical_limit + math.ceil(total * 0.3)

    for idx, task in enumerate(non_negative):
        if idx < critical_limit:
            mark(task, "critical")
        elif idx < important_limit:
            mark(task, "important")
        else:
            mark(task, "beneficial")

    for task in negative:
        mark(task, "rejected")


class TaskListView(LoginRequiredMixin, TemplateView):
    template_name = "tasks/task_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = Task.objects.with_metrics().order_by("-votes_score", "-updated_at")

        active_tasks = list(queryset.filter(status=Task.Status.ACTIVE))
        _assign_priorities(active_tasks)
        rejected_active = [task for task in active_tasks if task.priority_category == "rejected"]
        active_non_rejected = [task for task in active_tasks if task.priority_category != "rejected"]
        active_with_owner = [task for task in active_non_rejected if task.assigned_to]
        awaiting_tasks = [task for task in active_non_rejected if not task.assigned_to]
        finished_tasks = list(queryset.exclude(status=Task.Status.ACTIVE))
        _assign_priorities(finished_tasks)
        rejected_tasks = [task for task in finished_tasks if task.priority_category == "rejected"]
        completed_tasks = [
            task
            for task in finished_tasks
            if task.priority_category != "rejected" and task.status == Task.Status.COMPLETED
        ]
        cancelled_tasks = [
            task
            for task in finished_tasks
            if task.priority_category != "rejected" and task.status == Task.Status.CANCELLED
        ]

        context.update(
            {
                "active_tasks": active_with_owner,
                "awaiting_tasks": awaiting_tasks,
                "finished_completed": completed_tasks,
                "finished_rejected": rejected_tasks + rejected_active,
                "finished_cancelled": cancelled_tasks,
            }
        )
        return context


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"
    success_url = reverse_lazy("tasks:list")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, _("Task created."))
        return super().form_valid(form)


@require_POST
@login_required
def take_task(request: HttpRequest, pk: int) -> HttpResponse:
    task = get_object_or_404(Task, pk=pk)
    task.assigned_to = request.user
    task.save(update_fields=["assigned_to", "updated_at"])
    messages.success(
        request,
        _('Task "%(title)s" assigned to you.') % {"title": task.title},
    )
    return redirect(request.POST.get("next") or "tasks:list")


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = "tasks/task_detail.html"
    context_object_name = "task"

    def get_queryset(self):
        return Task.objects.with_metrics()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task = context["task"]
        if task.is_active:
            reference_tasks = list(
                Task.objects.with_metrics()
                .filter(status=Task.Status.ACTIVE)
                .order_by("-votes_score", "-updated_at")
            )
        else:
            reference_tasks = list(
                Task.objects.with_metrics()
                .exclude(status=Task.Status.ACTIVE)
                .order_by("-votes_score", "-updated_at")
            )
        _assign_priorities(reference_tasks)
        priority_map = {t.id: getattr(t, "priority_label", None) for t in reference_tasks}
        current_label = getattr(task, "priority_label", None)
        task.priority_label = priority_map.get(task.id, current_label or task.get_status_display())
        priority_map = {
            t.id: (
                getattr(t, "priority_label", None),
                getattr(t, "priority_category", None),
            )
            for t in reference_tasks
        }
        current_label, current_category = priority_map.get(
            task.id,
            (
                getattr(task, "priority_label", None),
                getattr(task, "priority_category", None),
            ),
        )
        task.priority_label = current_label or task.get_status_display()
        task.priority_category = current_category
        context["task"] = task
        return context


class TaskEditView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"

    def dispatch(self, request, *args, **kwargs):
        task = self.get_object()
        if task.assigned_to != request.user:
            messages.error(request, _("Only the current owner can edit this task."))
            return redirect("tasks:detail", pk=task.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        messages.success(self.request, _("Task updated."))
        return reverse_lazy("tasks:detail", kwargs={"pk": self.object.pk})


class TaskCloseView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskStatusForm
    template_name = "tasks/task_close.html"

    def dispatch(self, request, *args, **kwargs):
        task = self.get_object()
        if task.assigned_to != request.user:
            messages.error(request, _("Only the current owner can close this task."))
            return redirect("tasks:detail", pk=task.pk)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, _("Task closed."))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("tasks:detail", kwargs={"pk": self.object.pk})


@require_POST
@login_required
def vote_task(request: HttpRequest, pk: int) -> HttpResponse:
    task = get_object_or_404(Task, pk=pk)
    value = int(request.POST.get("value", 0))
    if value not in (TaskVote.Value.DOWN, TaskVote.Value.UP):
        messages.error(request, _("Invalid vote value."))
        return redirect(request.POST.get("next") or "tasks:list")

    vote, created = TaskVote.objects.get_or_create(
        task=task,
        user=request.user,
        defaults={"value": value},
    )
    if not created:
        vote.value = value
        vote.save(update_fields=["value", "updated_at"])
    messages.success(request, _("Vote saved."))
    return redirect(request.POST.get("next") or "tasks:list")


@require_POST
@login_required
def evaluate_task(request: HttpRequest, pk: int) -> HttpResponse:
    task = get_object_or_404(Task, pk=pk)
    value = request.POST.get("value")
    if value not in (
        TaskEvaluation.Value.SUCCESS,
        TaskEvaluation.Value.FAILURE,
    ):
        messages.error(request, _("Invalid evaluation choice."))
        return redirect(request.POST.get("next") or "tasks:list")

    evaluation, created = TaskEvaluation.objects.get_or_create(
        task=task,
        user=request.user,
        defaults={"value": value},
    )
    if not created:
        evaluation.value = value
        evaluation.save(update_fields=["value", "updated_at"])
    messages.success(request, _("Evaluation saved."))
    return redirect(request.POST.get("next") or "tasks:list")
