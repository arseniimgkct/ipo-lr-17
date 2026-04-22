from django.urls import path

from . import views


urlpatterns = [
    path("", views.home, name="index"),
    path("catalog/", views.catalog, name="catalog"),
    path("products/", views.catalog, name="product_list"),
    path("catalog/<int:pk>/", views.product_detail, name="product_detail"),
]
