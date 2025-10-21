# FarmaDeliveryProject/urls.py (Archivo principal del proyecto)

from django.contrib import admin
from django.urls import path, include
# --- ¡IMPORTACIONES NUEVAS PARA LAS IMÁGENES! ---
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Esta línea activa las funciones de Login y Logout
    path('accounts/', include('django.contrib.auth.urls')),
    
    # Esta línea incluye TODAS tus URLs de 'core' (home, buscar, perfil, etc.)
    path('', include('core.urls')),
    
    # La lista larga de URLs que tenías aquí se eliminó
    # porque ya estaba incluida en 'core.urls', lo que causaba duplicados.
]

# --- ¡CÓDIGO AÑADIDO AL FINAL! ---
# Esto le dice a Django cómo encontrar y servir las imágenes
# que subiste, pero SÓLO cuando DEBUG=True (en desarrollo).
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)