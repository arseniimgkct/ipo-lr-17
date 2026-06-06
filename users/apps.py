from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"

    def ready(self) -> None:
        from django.db.models.signals import post_save

        from .models import DefaultUser, create_profile_for_user

        post_save.connect(
            create_profile_for_user,
            sender=DefaultUser,
            dispatch_uid="users.create_profile_for_user",
        )
