# portal/views.py
from datetime import timezone as dt_tz
from urllib.parse import quote

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, ListView, DetailView, TemplateView

from .models import Event, EventRegistration, News, Lesson, StudyGroup
from .forms import ProfileForm, EventRegistrationForm


# ───────────── регистрация ──────────────
class SignUpView(CreateView):
    form_class = UserCreationForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('portal:login')


# ───────────── главная ──────────────
def index(request):
    # показываем 5 ближайших мероприятий и 5 последних новостей
    upcoming_events = Event.objects.filter(
        start_time__gte=timezone.now()
    ).order_by('start_time')[:5]

    latest_news = News.objects.order_by('-published')[:5]

    return render(
        request,
        'portal/index.html',
        {
            'upcoming': upcoming_events,
            'news_list': latest_news,
        },
    )


# ───────────── статические-пустышки ──────────────
def page1(request): return render(request, 'page1.html')
def page2(request): return render(request, 'page2.html')
def page3(request): return render(request, 'page3.html')
def page4(request): return render(request, 'page4.html')
def page5(request): return render(request, 'page5.html')


# ───────────── util: ссылка в Google Calendar ──────────────
def _gcal_link(event: Event) -> str:
    """Построить ссылку «Добавить в Google Calendar»."""
    start = event.start_time.astimezone(dt_tz.utc).strftime('%Y%m%dT%H%M%SZ')
    end = (
        event.end_time.astimezone(dt_tz.utc).strftime('%Y%m%dT%H%M%SZ')
        if event.end_time else ''
    )
    return (
        'https://calendar.google.com/calendar/render?action=TEMPLATE'
        f'&text={quote(event.title)}'
        f'&dates={start}/{end}'
        f'&details={quote(event.description or "")}'
    )


# ───────────── новости ──────────────
class NewsListView(ListView):
    model = News
    template_name = 'portal/news_list.html'
    context_object_name = 'news_list'
    ordering = ['-published']


class NewsDetailView(DetailView):
    model = News
    template_name = 'portal/news_detail.html'
    context_object_name = 'news'


# ───────────── мероприятия ──────────────
class EventListView(ListView):
    model = Event
    template_name = 'portal/events.html'
    context_object_name = 'events'
    ordering = ['start_time']


def event_detail(request, event_id: int):
    event = get_object_or_404(Event, pk=event_id)
    gcal = _gcal_link(event)

    registration = None
    if request.user.is_authenticated:
        registration = EventRegistration.objects.filter(
            event=event, user=request.user
        ).first()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'Авторизуйтесь, чтобы записаться')
            return redirect('portal:login')

        form = EventRegistrationForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data['role']
            if 'register' in request.POST:
                EventRegistration.objects.update_or_create(
                    event=event, user=request.user,
                    defaults={'role': role}
                )
                messages.success(request, 'Вы зарегистрированы!')
            elif 'unregister' in request.POST:
                EventRegistration.objects.filter(
                    event=event, user=request.user
                ).delete()
                messages.info(request, 'Регистрация отменена')
            return redirect('portal:event_detail', event_id=event.id)
    else:
        form = EventRegistrationForm(
            initial={'role': registration.role if registration else 'guest'}
        )

    return render(
        request, 'portal/event_detail.html',
        {
            'event': event,
            'gcal': gcal,
            'registration': registration,
            'form': form,
        },
    )


# ───────────── расписание ──────────────
class ScheduleView(LoginRequiredMixin, TemplateView):
    template_name = 'portal/schedule.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        groups = StudyGroup.objects.filter(students=self.request.user)
        context['lessons'] = (
            Lesson.objects
            .filter(group__in=groups)
            .select_related('group')
            .order_by('datetime')
        )
        return context


# ───────────── личный кабинет ──────────────
@login_required
def profile(request):
    registrations = (
        EventRegistration.objects
        .filter(user=request.user)
        .select_related('event')
        .order_by('event__start_time')
    )
    return render(request, 'profile.html', {'registrations': registrations})


@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль обновлён')
            return redirect('portal:profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'portal/profile_edit.html', {'form': form})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Пароль изменён')
            return redirect('portal:profile')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'portal/password_change.html', {'form': form})
