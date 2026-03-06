from django.contrib import admin
from .models import DefaultUser
    
@admin.register(DefaultUser)
class DefaultUserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email")
