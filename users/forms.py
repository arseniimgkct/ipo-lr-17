from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    UserChangeForm,
    UserCreationForm,
)

from .models import Profile, Role


User = get_user_model()


FORM_CONTROL_CLASS = "form-control auth-input"
FORM_SELECT_CLASS = "form-select auth-input"


class BootstrapFormMixin:
    """Добавляет Bootstrap-классы и базовые атрибуты ко всем полям формы."""

    def _apply_bootstrap(self):
        for name, field in self.fields.items():
            widget = field.widget
            css_class = (
                FORM_SELECT_CLASS
                if isinstance(widget, (forms.Select, forms.SelectMultiple))
                else FORM_CONTROL_CLASS
            )
            existing = widget.attrs.get("class", "")
            if css_class not in existing.split():
                widget.attrs["class"] = f"{existing} {css_class}".strip()
            widget.attrs.setdefault("autocomplete", "off")

    @property
    def helper_field_types(self):
        return {
            "email": {"type": "email", "autocomplete": "email"},
            "username": {"type": "text", "autocomplete": "username"},
            "full_name": {"type": "text", "autocomplete": "name"},
            "phone": {
                "type": "tel",
                "inputmode": "tel",
                "autocomplete": "tel",
            },
            "address": {"type": "text", "autocomplete": "street-address"},
            "delivery_city": {"type": "text", "autocomplete": "address-level2"},
            "delivery_index": {
                "type": "text",
                "inputmode": "numeric",
                "pattern": "[0-9]{4,10}",
            },
            "password": {"type": "password", "autocomplete": "current-password"},
            "password1": {"type": "password", "autocomplete": "new-password"},
            "password2": {"type": "password", "autocomplete": "new-password"},
            "old_password": {
                "type": "password",
                "autocomplete": "current-password",
            },
            "new_password1": {
                "type": "password",
                "autocomplete": "new-password",
            },
            "new_password2": {
                "type": "password",
                "autocomplete": "new-password",
            },
        }

    def _apply_field_types(self):
        types = self.helper_field_types
        for name, field in self.fields.items():
            attrs = types.get(name)
            if not attrs:
                continue
            for attr, value in attrs.items():
                field.widget.attrs.setdefault(attr, value)


class StyledAuthenticationForm(BootstrapFormMixin, AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap()
        self._apply_field_types()
        self.fields["username"].widget.attrs["placeholder"] = "demo"
        self.fields["password"].widget.attrs["placeholder"] = "••••••••"


class DefaultUserCreationForm(BootstrapFormMixin, UserCreationForm):
    email = forms.EmailField(
        label="Электронная почта",
        required=True,
        widget=forms.EmailInput(attrs={"placeholder": "you@example.com"}),
    )
    full_name = forms.CharField(
        label="ФИО",
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Иванов Иван"}),
    )
    phone = forms.CharField(
        label="Телефон",
        max_length=32,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "+375 (29) 123-45-67"}),
    )
    address = forms.CharField(
        label="Адрес доставки",
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "ул. Цветочная, 21"}),
    )
    delivery_city = forms.CharField(
        label="Город доставки",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Минск"}),
    )
    delivery_index = forms.CharField(
        label="Почтовый индекс",
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "220001", "inputmode": "numeric"}),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")
        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "username"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap()
        self._apply_field_types()
        self.fields["password1"].widget.attrs["placeholder"] = "Минимум 8 символов"
        self.fields["password2"].widget.attrs["placeholder"] = "Повторите пароль"
        self.fields["password1"].help_text = "Минимум 8 символов, не только цифры."
        self.fields["password2"].help_text = "Введите пароль ещё раз для подтверждения."

    def save(self, commit: bool = True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if not user.role:
            user.role = Role.CUSTOMER
        if commit:
            user.save()
        profile, _ = Profile.objects.get_or_create(user=user)
        profile.full_name = self.cleaned_data.get("full_name", "")
        profile.phone = self.cleaned_data.get("phone", "")
        profile.address = self.cleaned_data.get("address", "")
        profile.delivery_city = self.cleaned_data.get("delivery_city", "")
        profile.delivery_index = self.cleaned_data.get("delivery_index", "")
        profile.save()
        return user


class DefaultUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ("username", "email", "role")


class ProfileForm(BootstrapFormMixin, forms.ModelForm):
    email = forms.EmailField(
        label="Электронная почта",
        required=True,
        widget=forms.EmailInput(attrs={"placeholder": "you@example.com"}),
    )
    role = forms.ChoiceField(
        label="Роль",
        choices=Role.choices,
        widget=forms.Select(attrs={"class": FORM_SELECT_CLASS}),
    )

    class Meta:
        model = Profile
        fields = (
            "full_name",
            "phone",
            "address",
            "delivery_city",
            "delivery_index",
        )
        widgets = {
            "full_name": forms.TextInput(
                attrs={"placeholder": "Иванов Иван", "class": FORM_CONTROL_CLASS}
            ),
            "phone": forms.TextInput(
                attrs={
                    "placeholder": "+375 (29) 123-45-67",
                    "class": FORM_CONTROL_CLASS,
                }
            ),
            "address": forms.TextInput(
                attrs={"placeholder": "ул. Цветочная, 21", "class": FORM_CONTROL_CLASS}
            ),
            "delivery_city": forms.TextInput(
                attrs={"placeholder": "Минск", "class": FORM_CONTROL_CLASS}
            ),
            "delivery_index": forms.TextInput(
                attrs={
                    "placeholder": "220001",
                    "class": FORM_CONTROL_CLASS,
                    "inputmode": "numeric",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields["email"].initial = user.email
            self.fields["email"].widget.attrs["placeholder"] = "you@example.com"
            self.fields["role"].initial = user.role
            if not (getattr(user, "is_admin_role", False) or user.is_superuser):
                self.fields["role"].disabled = True
                self.fields["role"].help_text = (
                    "Только администратор может менять роль."
                )
        for name in ("full_name", "phone", "address", "delivery_city", "delivery_index"):
            if name in self.fields:
                self.fields[name].required = False
        self._apply_field_types()

    def save(self, commit: bool = True):
        profile = super().save(commit=False)
        user = profile.user
        user.email = self.cleaned_data.get("email") or user.email
        if (getattr(user, "is_admin_role", False) or user.is_superuser) and "role" in self.cleaned_data:
            user.role = self.cleaned_data["role"]
        if commit:
            user.save()
            profile.save()
        return profile


class StyledPasswordChangeForm(BootstrapFormMixin, PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap()
        self._apply_field_types()
        self.fields["old_password"].widget.attrs["placeholder"] = "Текущий пароль"
        self.fields["new_password1"].widget.attrs["placeholder"] = "Новый пароль"
        self.fields["new_password2"].widget.attrs["placeholder"] = "Повторите новый пароль"
