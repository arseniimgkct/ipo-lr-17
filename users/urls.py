from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import StyledAuthenticationForm


urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="registration/login.html",
            authentication_form=StyledAuthenticationForm,
        ),
        name="login",
    ),
    path("api/me/", views.ProfileAPIView.as_view(), name="api_me"),
    path("api/orders/", views.OrdersAPIView.as_view(), name="api_orders"),
    path("api/orders/<int:pk>/", views.OrderDetailAPIView.as_view(), name="api_order_detail"),
    path("account/", views.personal_cabinet, name="personal_cabinet"),
    path("account/settings/", views.account_settings, name="account_settings"),
    path("account/orders/<int:pk>/", views.order_detail, name="order_detail"),
]
