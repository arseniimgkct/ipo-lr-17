from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.contrib import admin

from .forms import DefaultUserCreationForm, DefaultUserChangeForm
from .models import DefaultUser


class DefaultUserAdmin(UserAdmin):
    add_form = DefaultUserCreationForm
    form = DefaultUserChangeForm
    model = DefaultUser
    list_display = ['email', 'username',]


admin.site.register(DefaultUser, DefaultUserAdmin)
