from django.contrib import admin
from .models import StudyGroup, News, Event, Lesson


@admin.register(StudyGroup)
class StudyGroupAdmin(admin.ModelAdmin):
    list_display = ("name",)               # Показываем только поле name
    search_fields = ("name",)
    filter_horizontal = ("students",)      # Название поля ManyToMany — students


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ("title", "published")
    list_filter = ("published",)
    search_fields = ("title",)
    readonly_fields = ("published",)       # Поля created/updated нет


from django.contrib import admin
from .models import Event, EventRegistration


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "start_time", "created")
    readonly_fields = ("created",)
    search_fields = ("title", "description")
    list_filter = ("start_time",)
    ordering = ("start_time",)


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ("event", "user", "role")
    list_filter = ("role",)
    search_fields = ("event__title", "user__username")


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "datetime", "group")
    list_filter = ("group",)
    search_fields = ("title",)
    autocomplete_fields = ("group",)       # Для ForeignKey
