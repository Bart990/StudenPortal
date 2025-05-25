# portal/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


# ─────────────────────────── Мероприятия ────────────────────────────
class Event(models.Model):
    """
    Мероприятие, отображается в календаре/списке событий.
    """
    title       = models.CharField(_("Название"), max_length=200)
    description = models.TextField(_("Описание"), blank=True)
    start_time  = models.DateTimeField(_("Дата и время начала"))
    end_time    = models.DateTimeField(
        _("Дата и время окончания"), null=True, blank=True
    )
    created     = models.DateTimeField(_("Создано"), auto_now_add=True)

    class Meta:
        ordering = ["start_time"]
        verbose_name = _("Мероприятие")
        verbose_name_plural = _("Мероприятия")

    def __str__(self):
        return self.title


class EventRegistration(models.Model):
    """
    Запись пользователя на мероприятие с выбранной ролью.
    (event, user) — уникальная пара.
    """

    class Role(models.TextChoices):
        GUEST       = "guest",       _("Гость")
        PARTICIPANT = "participant", _("Участник")
        ORGANIZER   = "organizer",   _("Организатор")

    event = models.ForeignKey(
        Event,
        verbose_name=_("Мероприятие"),
        related_name="registrations",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Пользователь"),
        on_delete=models.CASCADE,
    )
    role = models.CharField(
        _("Роль"),
        max_length=20,
        choices=Role.choices,
        default=Role.GUEST,
    )

    class Meta:
        unique_together = ("event", "user")
        verbose_name = _("Регистрация на мероприятие")
        verbose_name_plural = _("Регистрации на мероприятия")

    def __str__(self):
        return f"{self.user} — {self.event} ({self.get_role_display()})"


# ─────────────────────────── Учебные группы ─────────────────────────
class StudyGroup(models.Model):
    """
    Учебная группа; студенты связываются ManyToMany-полем.
    """
    name     = models.CharField(_("Название группы"), max_length=100, unique=True)
    students = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Студенты"),
        related_name="study_groups",
        blank=True,
    )

    class Meta:
        verbose_name = _("Учебная группа")
        verbose_name_plural = _("Учебные группы")

    def __str__(self):
        return self.name


# ─────────────────────────── Новости ────────────────────────────────
class News(models.Model):
    """
    Новости портала.
    """
    title     = models.CharField(_("Заголовок новости"), max_length=200)
    body      = models.TextField(_("Текст новости"))
    published = models.DateTimeField(
        _("Дата и время публикации"),
        default=timezone.now,
        help_text=_("Будет установлено текущее время"),
    )

    class Meta:
        ordering = ("-published",)
        verbose_name = _("Новость")
        verbose_name_plural = _("Новости")

    def __str__(self):
        return self.title


# ─────────────────────────── Расписание (занятия) ───────────────────
class Lesson(models.Model):
    """
    Занятие, показывается в расписании группы.
    """
    title    = models.CharField(_("Тема занятия"), max_length=200)
    datetime = models.DateTimeField(_("Дата и время занятия"))
    group    = models.ForeignKey(
        StudyGroup,
        verbose_name=_("Группа"),
        related_name="lessons",
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ("datetime",)
        verbose_name = _("Занятие")
        verbose_name_plural = _("Занятия")

    def __str__(self):
        return f"{self.datetime:%d.%m.%Y %H:%M} — {self.title}"


# ─────────────────────────── Профиль пользователя ───────────────────
class Profile(models.Model):
    """
    Расширяет стандартного пользователя дополнительными полями.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    bio = models.TextField(_("О себе"), blank=True)

    class Meta:
        verbose_name = _("Профиль")
        verbose_name_plural = _("Профили")

    def __str__(self):
        return f"Profile of {self.user.username}"
