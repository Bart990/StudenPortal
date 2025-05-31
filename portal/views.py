# portal/views.py
from urllib.parse import quote
from datetime import timezone as dt_tz

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView, ListView, DetailView, TemplateView
)

from .forms import ProfileForm, EventRegistrationForm
from .models import (
    Event, EventRegistration, News,
    Lesson, StudyGroup
)

# ─────────────────────────  util  ──────────────────────────
def _gcal_link(event: Event) -> str:
    """Построить ссылку «Добавить в Google Календарь»."""
    start = event.start_time.astimezone(dt_tz.utc).strftime("%Y%m%dT%H%M%SZ")
    end = (
        event.end_time.astimezone(dt_tz.utc).strftime("%Y%m%dT%H%M%SZ")
        if event.end_time else ""
    )
    return (
        "https://calendar.google.com/calendar/render?action=TEMPLATE"
        f"&text={quote(event.title)}"
        f"&dates={start}/{end}"
        f"&details={quote(event.description or '')}"
    )

# ─────────────────────────  auth / signup  ─────────────────
class SignUpView(CreateView):
    form_class = UserCreationForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("portal:login")

# ─────────────────────────  index  ─────────────────────────
def index(request):
    upcoming = Event.objects.filter(
        start_time__gte=timezone.now()
    ).order_by("start_time")[:5]

    latest_news = News.objects.order_by("-published")[:5]

    return render(
        request,
        "portal/index.html",
        {"upcoming": upcoming, "news_list": latest_news},
    )

# ─────────────────────────  static stubs  ──────────────────
def page1(r): return render(r, "page1.html")
def page2(r): return render(r, "page2.html")
def page3(r): return render(r, "page3.html")
def page4(r): return render(r, "page4.html")
def page5(r): return render(r, "page5.html")

# ─────────────────────────  news  ──────────────────────────
class NewsListView(ListView):
    model = News
    template_name = "portal/news_list.html"
    paginate_by = 10
    context_object_name = "news_list"

    def get_queryset(self):
        qs = super().get_queryset().order_by("-published")
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(body__icontains=q))
        return qs


class NewsDetailView(DetailView):
    model = News
    template_name = "portal/news_detail.html"
    context_object_name = "news"

# ─────────────────────────  events  ────────────────────────
class EventListView(ListView):
    model = Event
    template_name = "portal/events.html"
    context_object_name = "event_list"
    paginate_by = 10

    def get_queryset(self):
        return (
            Event.objects
            .filter(start_time__gte=timezone.now())
            .order_by("start_time")
        )


class EventDetailView(DetailView):
    """CBV-замена старой FBV `event_detail` с поддержкой регистрации."""
    model = Event
    template_name = "portal/event_detail.html"
    context_object_name = "event"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        event: Event = self.object
        user = self.request.user
        reg = (
            EventRegistration.objects
            .filter(event=event, user=user)
            .first() if user.is_authenticated else None
        )
        ctx.update({
            "gcal": _gcal_link(event),
            "registration": reg,
            "form": EventRegistrationForm(
                initial={"role": reg.role if reg else "guest"}
            ),
        })
        return ctx

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()          # загружаем event
        if not request.user.is_authenticated:
            messages.error(request, "Авторизуйтесь, чтобы записаться")
            return redirect("portal:login")

        form = EventRegistrationForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data["role"]
            if "register" in request.POST:
                EventRegistration.objects.update_or_create(
                    event=self.object, user=request.user,
                    defaults={"role": role}
                )
                messages.success(request, "Вы зарегистрированы!")
            elif "unregister" in request.POST:
                EventRegistration.objects.filter(
                    event=self.object, user=request.user
                ).delete()
                messages.info(request, "Регистрация отменена")
        return redirect("portal:event_detail", pk=self.object.pk)

# ─────────────────────────  schedule  ──────────────────────
class ScheduleView(LoginRequiredMixin, TemplateView):
    template_name = "portal/schedule.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        groups = StudyGroup.objects.filter(students=self.request.user)
        ctx["lessons"] = (
            Lesson.objects.filter(group__in=groups)
            .select_related("group")
            .order_by("datetime")
        )
        return ctx

# ─────────────────────────  profile  ───────────────────────
@login_required
def profile(request):
    registrations = (
        EventRegistration.objects.filter(user=request.user)
        .select_related("event")
        .order_by("event__start_time")
    )
    return render(request, "profile.html", {"registrations": registrations})


@login_required
def profile_edit(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль обновлён")
            return redirect("portal:profile")
    else:
        form = ProfileForm(instance=request.user)
    return render(request, "portal/profile_edit.html", {"form": form})


@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Пароль изменён")
            return redirect("portal:profile")
    else:
        form = PasswordChangeForm(request.user)
    return render(request, "portal/password_change.html", {"form": form})

# ─────────────────────────  unions  ────────────────────────
def unions_list(request):
    unions = [
        "Культурно-массовое направление",
        "Культурно-Массовый комитет",
        "Студенческое творческое общество",
        "Спортивный комитет",
        "Language Club",
        "Клуб болельщиков",
        "Социально-правовое направление",
        "Комитет помощи студентам",
        "Социальный комитет",
        "Абитуриент-Club",
        "Buddy System",
        "Студенческий совет общежитий",
        "Информационно-коммуникационное направление",
        "Аналитический центр",
        "First Fresh Media",
        "Центр внешних связей и коммуникаций",
        "IT-Center",
        "Секретарская академия",
    ]
    return render(request, "portal/unions.html", {"unions": unions})
