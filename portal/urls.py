from django.urls import path
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from . import views
from .views import EventListView, EventDetailView

app_name = "portal"

urlpatterns = [
    path("", views.index, name="home"),

    # ─── пять пустых страниц
    path("history/", views.page1, name="page1"),
    path("studsov/", views.page2, name="page2"),
    path("contactpriem/", views.page3, name="page3"),
    path("capitans/", views.page4, name="page4"),
    path("plechanovka/", views.page5, name="page5"),

    # ─── новости
    path("news/", views.NewsListView.as_view(),      name="news"),
    path("news_list/", views.NewsListView.as_view(),      name="news_list"),
    path("news/<int:pk>/", views.NewsDetailView.as_view(), name="news_detail"),

    # ─── мероприятия
    path("events/", EventListView.as_view(), name="events"),
    path("event/<int:pk>/", EventDetailView.as_view(), name="event_detail"),

    # ─── расписание
    path("schedule/", views.ScheduleView.as_view(), name="schedule"),

    # ─── личный кабинет
    path("profile/",           views.profile,        name="profile"),
    path("profile/edit/",      views.profile_edit,   name="profile_edit"),
    path("profile/password/",  views.change_password,name="change_password"),

    # ─── auth
    path("login/",  auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="portal:home"),                name="logout"),
    path("signup/", views.SignUpView.as_view(),                                           name="signup"),

    # ─── инфо
    path("contacts/", TemplateView.as_view(template_name="contacts.html"), name="contacts"),
    path("about/",    TemplateView.as_view(template_name="about.html"),    name="about"),
    path("faq/",      TemplateView.as_view(template_name="faq.html"),      name="faq"),

    path("unions/", views.unions_list, name="unions"),
]
