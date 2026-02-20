from django.contrib import admin
from django.urls import path, include
from .views import index, about


urlpatterns = [
    path('', index),
    path('panel/', include("panel.urls")),
    path('flowers/', include("flowers.urls")),
    path('about/', about),
    path('admin/', admin.site.urls),
]
