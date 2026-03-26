import logging
from django.core.management.base import BaseCommand
from chat.models import Room
from tasks.models import Task

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Backfill chat_room FK for existing tasks that have a matching room by title"

    def handle(self, *args, **options):
        tasks = Task.objects.filter(chat_room__isnull=True)
        linked = 0
        missing = 0

        for task in tasks:
            title = task.get_chat_room_title()
            room = Room.objects.filter(title=title).first()
            if room:
                Task.objects.filter(pk=task.pk).update(chat_room=room)
                self.stdout.write(f"  Linked task #{task.id} -> room '{title}'")
                linked += 1
            else:
                self.stdout.write(self.style.WARNING(f"  No room found for task #{task.id}: '{title}'"))
                missing += 1

        self.stdout.write(self.style.SUCCESS(
            f"Done. Linked: {linked}, no room found: {missing}"
        ))
