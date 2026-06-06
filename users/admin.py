from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import DefaultUserChangeForm, DefaultUserCreationForm
from .models import Profile


User = get_user_model()


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    extra = 0
    fields = (
        "full_name",
        "phone",
        "address",
        "delivery_city",
        "delivery_index",
    )


class DefaultUserAdmin(UserAdmin):
    add_form = DefaultUserCreationForm
    form = DefaultUserChangeForm
    model = User
    list_display = ("email", "username", "role", "is_staff")
    list_filter = ("role", "is_staff", "is_superuser")
    fieldsets = UserAdmin.fieldsets + (
        ("Роль и профиль", {"fields": ("role",)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Роль", {"fields": ("role",)}),
    )
    inlines = (ProfileInline,)


admin.site.register(User, DefaultUserAdmin)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "full_name", "phone", "delivery_city", "delivery_index")
    search_fields = ("user__username", "user__email", "full_name", "phone")
