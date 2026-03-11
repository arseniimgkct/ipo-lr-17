from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import DefaultUser


class DefaultUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = DefaultUser
        fields = ('username', 'email')


class DefaultUserChangeForm(UserChangeForm):

    class Meta:
        model = DefaultUser
        fields = ('username', 'email')
