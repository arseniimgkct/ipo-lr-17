from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart_view, name="cart_view"),
    path('add/<int:pk>/', views.add_to_cart, name="add_to_cart"),
    path('update/<int:product_id>/', views.update_cart, name="update_cart"),
    path('remove/<int:item_id>/', views.cart_view, name='cart_view'),
]
