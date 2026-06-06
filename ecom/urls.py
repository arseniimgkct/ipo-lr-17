from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from cart.views import CartViewSet
from catalog.views import CategoryViewSet, ProducerViewSet, ProductViewSet
from users.views import OrderDetailAPIView, OrdersAPIView, ProfileAPIView


router = DefaultRouter()
router.register(r"products", ProductViewSet, basename="products")
router.register(r"categories", CategoryViewSet, basename="categories")
router.register(r"producers", ProducerViewSet, basename="producers")
router.register(r"cart", CartViewSet, basename="cart")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("catalog.urls")),
    path("cart/", include("cart.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/", include("users.urls")),
    path("api/me/", ProfileAPIView.as_view(), name="api_me_root"),
    path("api/orders/", OrdersAPIView.as_view(), name="api_orders_root"),
    path("api/orders/<int:pk>/", OrderDetailAPIView.as_view(), name="api_order_detail_root"),
    path("api/", include(router.urls)),
    path("api-token-auth/", obtain_auth_token, name="api-token-auth"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
