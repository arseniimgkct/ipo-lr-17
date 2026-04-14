from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from catalog.views import ProductViewSet, CategoryViewSet, ProducerViewSet
from cart.views import CartViewSet

router = DefaultRouter()

router.register(r'products', ProductViewSet, basename='products')
router.register(r'categories', CategoryViewSet)
router.register(r'producers', ProducerViewSet)
router.register(r'cart', CartViewSet, basename='cart')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api-token-auth/', obtain_auth_token),
]