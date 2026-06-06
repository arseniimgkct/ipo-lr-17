from django.contrib import messages
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from checkout.models import Checkout

from .forms import (
    DefaultUserCreationForm,
    ProfileForm,
    StyledAuthenticationForm,
    StyledPasswordChangeForm,
)
from .models import DefaultUser, Profile, Role
from .serializers import OrderSerializer, ProfileSerializer


class IsAuthenticated401(permissions.IsAuthenticated):
    """Возвращает 401 для неавторизованных (даже через session auth)."""

    def authenticate_header(self, request):
        return 'Token realm="api"'


# -----------------------------
# Session-based views (HTML)
# -----------------------------


@require_http_methods(["GET", "POST"])
def signup(request):
    if request.user.is_authenticated:
        return redirect("personal_cabinet")
    if request.method == "POST":
        form = DefaultUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Добро пожаловать в Bloom Boutique!")
            return redirect("personal_cabinet")
    else:
        form = DefaultUserCreationForm()
    return render(request, "registration/signup.html", {"form": form})


@login_required
def personal_cabinet(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    orders_qs = (
        Checkout.objects.filter(user=request.user)
        .order_by("-created_at")
    )
    if not request.user.is_admin_role:
        orders_qs = orders_qs.filter(user=request.user)
    return render(
        request,
        "account/profile.html",
        {
            "profile": profile,
            "orders": orders_qs,
            "is_admin": request.user.is_admin_role,
        },
    )


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Checkout, pk=pk)
    if order.user_id != request.user.id and not request.user.is_admin_role:
        messages.error(request, "У вас нет доступа к этому заказу.")
        return redirect("personal_cabinet")
    return render(request, "account/order_detail.html", {"order": order})


@login_required
@require_http_methods(["GET", "POST"])
def account_settings(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        action = request.POST.get("action", "profile")

        if action == "password":
            password_form = StyledPasswordChangeForm(request.user, request.POST)
            profile_form = ProfileForm(instance=profile, user=request.user)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Пароль успешно обновлён.")
                return redirect("account_settings")
            return render(
                request,
                "account/settings.html",
                {
                    "profile_form": profile_form,
                    "password_form": password_form,
                    "profile": profile,
                },
            )

        profile_form = ProfileForm(request.POST, instance=profile, user=request.user)
        password_form = StyledPasswordChangeForm(request.user)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, "Профиль обновлён.")
            return redirect("account_settings")
        return render(
            request,
            "account/settings.html",
            {
                "profile_form": profile_form,
                "password_form": password_form,
                "profile": profile,
            },
        )

    profile_form = ProfileForm(instance=profile, user=request.user)
    password_form = StyledPasswordChangeForm(request.user)
    return render(
        request,
        "account/settings.html",
        {
            "profile_form": profile_form,
            "password_form": password_form,
            "profile": profile,
        },
    )


# -----------------------------
# API views (DRF)
# -----------------------------


class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated401]

    def get(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        return Response(ProfileSerializer(profile).data)

    def patch(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrdersAPIView(APIView):
    permission_classes = [IsAuthenticated401]

    def get(self, request):
        qs = Checkout.objects.order_by("-created_at")
        if not request.user.is_admin_role:
            qs = qs.filter(user=request.user)
        elif request.query_params.get("all") == "1" and request.user.is_admin_role:
            qs = Checkout.objects.order_by("-created_at")
        return Response(OrderSerializer(qs, many=True).data)


class OrderDetailAPIView(APIView):
    permission_classes = [IsAuthenticated401]

    def get(self, request, pk):
        order = get_object_or_404(Checkout, pk=pk)
        if order.user_id != request.user.id and not request.user.is_admin_role:
            return Response(
                {"detail": "Заказ не найден."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(OrderSerializer(order).data)
