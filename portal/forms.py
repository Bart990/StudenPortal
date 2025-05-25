from django import forms
from django.contrib.auth import get_user_model

from .models import EventRegistration

User = get_user_model()


class ProfileForm(forms.ModelForm):
    class Meta:
        model  = User
        fields = ["first_name", "last_name", "email"]


class EventRegistrationForm(forms.Form):
    ROLE_CHOICES = (
        ("guest",     "Гость"),
        ("participant", "Участник"),
        ("organizer", "Организатор"),
    )
    role = forms.ChoiceField(choices=ROLE_CHOICES, label="Ваша роль")
