from datetime import datetime, timedelta
from glosowania.models import Decyzja, ZebranePodpisy, KtoJuzGlosowal, VoteCode
from glosowania.forms import DecyzjaForm
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.http import HttpRequest
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.core.mail import EmailMessage
from django.conf import settings as s
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import redirect
import logging
from django.utils import translation
import threading
import random
from chat.models import Room
from zzz.utils import get_site_domain

l = logging.getLogger(__name__)

HOST = get_site_domain()

@login_required
def dodaj(request: HttpRequest):
    # Dodaj nową propozycję przepisu:
    # nowy = DecyzjaForm(request.POST or None)
    if request.method == 'POST':
        form = DecyzjaForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.author = request.user
            form.data_powstania = datetime.today()
            # form.ile_osob_podpisalo += 1
            form.status = 1
            form.path = _("Proposition")
            form.save()
            # signed = ZebranePodpisy.objects.create(projekt=form, podpis_uzytkownika = request.user)
            
            l.info(f"New proposal {form.id} added by {form.author}")
            message = _("New proposal has been saved.")
            messages.success(request, (message))

            SendEmail(
                _('New law proposal'),
                _('{user} added new law proposal\nYou can read it here: {url}').format(
                    user=request.user.username.capitalize(),
                    url=f'http://{HOST}/glosowania/details/{str(form.id)}'
                )
            )
            return redirect('glosowania:proposition')
        else:
            return render(request, 'glosowania/dodaj.html', {'form': form})
    else:
        form = DecyzjaForm()
    return render(request, 'glosowania/dodaj.html', {'form': form})


@login_required
def edit(request: HttpRequest, pk: int):
    decision = Decyzja.objects.get(pk=pk)

    if request.method == 'POST':
        form = DecyzjaForm(request.POST)
        if form.is_valid():
            decision.author = request.user # type: ignore
            decision.title = form.cleaned_data['title']
            decision.tresc = form.cleaned_data['tresc']
            decision.kara = form.cleaned_data['kara']
            decision.uzasadnienie = form.cleaned_data['uzasadnienie']
            decision.args_for = form.cleaned_data['args_for']
            decision.args_against = form.cleaned_data['args_against']
            decision.znosi = form.cleaned_data['znosi']
            decision.save()
            message = _("Saved.")
            messages.success(request, (message))

            SendEmail(
                _("Proposal no. {} has been modified").format(decision.id),
                _('{user} modified proposal\nYou can read new version here: {url}').format(
                    user=request.user.username.capitalize(),
                    url=f'http://{HOST}/glosowania/details/{str(decision.id)}'
                )
            )
            return redirect('glosowania:proposition')
    else:  # request.method != 'POST':
        form = DecyzjaForm(initial={
            'author': decision.author,
            'title': decision.title,
            'tresc': decision.tresc,
            'kara': decision.kara,
            'uzasadnienie': decision.uzasadnienie,
            'args_for': decision.args_for,
            'args_against': decision.args_against,
            'znosi': decision.znosi,
        })
        
    # l.info(f"Proposal {decision.id} modified by {request.user}") # Can't log that because it kicks in on form open (not on save)
    return render(request, 'glosowania/edit.html', {'form': form})


def generate_code():
    return''.join([random.SystemRandom().choice('abcdefghjkmnoprstuvwxyz23456789') for i in range(5)])


@login_required
def details(request:HttpRequest, pk: int):
    # Pokaż szczegóły przepisu

    szczegoly = get_object_or_404(Decyzja, pk=pk)

    if request.GET.get('sign'):
        nowy_projekt = Decyzja.objects.get(pk=pk)
        osoba_podpisujaca = request.user
        podpis = ZebranePodpisy(projekt=nowy_projekt, podpis_uzytkownika=osoba_podpisujaca)
        nowy_projekt.ile_osob_podpisalo += 1
        podpis.save()
        nowy_projekt.save()
        message = _('You signed this motion for a referendum.')
        messages.success(request, (message))
        return redirect('glosowania:details', pk)

    if request.GET.get('withdraw'):
        nowy_projekt = Decyzja.objects.get(pk=pk)
        osoba_podpisujaca = request.user
        podpis = ZebranePodpisy.objects.get(projekt=nowy_projekt, podpis_uzytkownika=osoba_podpisujaca)
        podpis.delete()
        nowy_projekt.ile_osob_podpisalo -= 1
        nowy_projekt.save()
        message = _('Not signed.')
        messages.success(request, (message))
        return redirect('glosowania:details', pk)

    if request.GET.get('tak'):
        nowy_projekt = Decyzja.objects.get(pk=pk)
        osoba_glosujaca = request.user
        glos = KtoJuzGlosowal(
                              projekt=nowy_projekt,
                              ktory_uzytkownik_juz_zaglosowal=osoba_glosujaca
                             )
        nowy_projekt.za += 1
        glos.save()
        nowy_projekt.save()
        
        # TODO: Kod oddanego głosu
        # - wygeneruj kod
        # - tak
        # - projekt
        # - zapisz
        # - wyswietl
        code = generate_code()
        report = VoteCode.objects.create(project=nowy_projekt, code=code, vote=True)

        message1 = str(_('Your vote has been saved. You voted Yes.'))
        messages.success(request, (message1))

        message2 = f"{_('Your verification code is:')} {code}"
        messages.error(request, (message2))

        message3 = str(_('Write down your code or create screenshot to verify it when the referendum is over. This code will be presented just once and will be not related to you.'))
        messages.info(request, (message3))

        return redirect('glosowania:details', pk)

    if request.GET.get('nie'):
        nowy_projekt = Decyzja.objects.get(pk=pk)
        osoba_glosujaca = request.user
        glos = KtoJuzGlosowal(projekt=nowy_projekt, ktory_uzytkownik_juz_zaglosowal=osoba_glosujaca)
        nowy_projekt.przeciw += 1
        glos.save()
        nowy_projekt.save()

        # TODO: Kod oddanego głosu
        # - wygeneruj kod
        # - nie
        # - projekt
        # - zapisz
        # - wyswietl
        code = generate_code()
        report = VoteCode.objects.create(project=nowy_projekt, code=code, vote=False)

        message1 = str(_('Your vote has been saved. You voted No.'))
        messages.success(request, (message1))

        message2 = f"{_('Your verification code is:')} {code}"
        messages.error(request, (message2))

        message3 = str(_('Write down your code or create screenshot to verify it when the referendum is over. This code will be presented just once and will be not related to you.'))
        messages.info(request, (message3))

        return redirect('glosowania:details', pk)

    # check if already signed
    signed = ZebranePodpisy.objects.filter(projekt=pk, podpis_uzytkownika=request.user).exists()

    # check if already voted
    voted = KtoJuzGlosowal.objects.filter(projekt=pk, ktory_uzytkownik_juz_zaglosowal=request.user).exists()

    # Report
    report = VoteCode.objects.filter(project_id=pk).order_by('vote', 'code')

    # List of voters
    voters = KtoJuzGlosowal.objects.filter(projekt=pk).select_related('ktory_uzytkownik_juz_zaglosowal').order_by('ktory_uzytkownik_juz_zaglosowal__username')

    # State dictionary
    state = {1: _('Proposition'), 2: _('Discussion'), 3: _('Referendum'), 4: _('Rejected'), 5: _('Approved'), }

    # Previous and Next
    obj = get_object_or_404(Decyzja, pk=pk)
    prev = Decyzja.objects.filter(pk__lt=obj.pk, status = szczegoly.status).order_by('-pk').first()
    next = Decyzja.objects.filter(pk__gt=obj.pk, status = szczegoly.status).order_by('pk').first()
    
    # Find associated chat room
    room_title = f"#{szczegoly.pk}:{szczegoly.title[:20]}"

    chat_room = Room.objects.filter(title=room_title).first()
    
    return render(request, 'glosowania/szczegoly.html', {'id': szczegoly,
                                                         'signed': signed,
                                                         'voted': voted,
                                                         'report': report,
                                                         'voters': voters,
                                                         'current_user': request.user,
                                                         'state': state[szczegoly.status],
                                                         'data_referendum_stop': szczegoly.data_referendum_stop,
                                                         'prev': prev,
                                                         'next': next,
                                                         'chat_room': chat_room,
                                                         })


def SendEmail(subject: str, message: str):
    # bcc: all active users
    # subject: Custom
    # message: Custom
    translation.activate(s.LANGUAGE_CODE)

    email_message = EmailMessage(
        from_email=str(s.DEFAULT_FROM_EMAIL),
        bcc = list(User.objects.filter(is_active=True).values_list('email', flat=True)),
        subject=f'[{HOST}] {subject}',
        body=message + "\n\n" + _("Why you received this email? Here is explanation: https://wikikracja.pl/powiadomienia-email/"),
        )
    # l.info(f'subject: {subject} \n message: {message}')
    
    t = threading.Thread(
        target=email_message.send,
        kwargs={"fail_silently": False,}
    )
    t.setDaemon(True)
    t.start()

# proposition = 1
# discussion = 2
# referendum = 3
# rejected = 4
# approved = 5


@login_required
def parameters(request: HttpRequest):
    return render(request, 'glosowania/parameters.html', {
        'signatures': s.WYMAGANYCH_PODPISOW,
        'signatures_span': timedelta(days=s.CZAS_NA_ZEBRANIE_PODPISOW).days,
        'queue_span': timedelta(days=s.DYSKUSJA).days,
        'referendum_span': timedelta(days=s.CZAS_TRWANIA_REFERENDUM).days,
    })


@login_required
def rejected(request: HttpRequest):
    votings = Decyzja.objects.filter(status=4).order_by('id')
    return render(request, 'glosowania/rejected.html', {'votings': votings})


@login_required
def proposition(request: HttpRequest):
    votings = Decyzja.objects.filter(status=1).order_by('data_referendum_start')
    return render(request, 'glosowania/proposition.html', {'votings': votings})


@login_required
def discussion(request: HttpRequest):
    votings = Decyzja.objects.filter(status=2).order_by('data_referendum_start')
    return render(request, 'glosowania/discussion.html', {'votings': votings})


@login_required
def referendum(request: HttpRequest):
    votings = Decyzja.objects.filter(status=3).order_by('data_referendum_start')
    return render(request, 'glosowania/referendum.html', {'votings': votings})


@login_required
def approved(request: HttpRequest):
    votings = Decyzja.objects.filter(status=5).order_by('data_referendum_start')
    return render(request, 'glosowania/approved.html', {'votings': votings})
