# FarmaDeliveryProject/urls.py (Archivo principal del proyecto)

from django.contrib import admin
from django.urls import path, include
from core import views as core_views # Importamos la vista 'home_page' de tu app 'core'
urlpatterns = [
    path('admin/', admin.site.urls),
    # Esta línea activa las funciones de Login y Logout
    path('accounts/', include('django.contrib.auth.urls')),
    
    path('', core_views.home_page, name='home'), # Usamos la vista 'home_page' como la página de inicio
]