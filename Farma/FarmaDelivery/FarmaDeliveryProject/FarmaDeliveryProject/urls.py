# FarmaDeliveryProject/urls.py (Archivo principal del proyecto)

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Esta línea activa las funciones de Login y Logout
    path('accounts/', include('django.contrib.auth.urls')),
    # Incluir todas las URLs de la app core
    path('', include('core.urls')),
]
