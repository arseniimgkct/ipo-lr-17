from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
import os

urlpatterns = [
    path('', views.index, name="index"),
    path('admin/', admin.site.urls, name="admin"),
    path('catalog/', include('catalog.urls')),
    path('cart/', include('cart.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('users.urls')),
    path('checkout/', include('checkout.urls'))    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
