from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('admin/', admin.site.urls, name="admin"),
    path('catalog/', include('catalog.urls')),
    path('cart/', include('cart.urls')),
]
