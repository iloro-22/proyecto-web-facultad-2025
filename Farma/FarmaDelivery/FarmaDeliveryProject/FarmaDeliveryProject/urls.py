# FarmaDeliveryProject/urls.py (Archivo principal del proyecto)

from re import DEBUG
from django.contrib import admin
from django.urls import path, include
from core import views as core_views # Importamos la vista 'home_page' de tu app 'core'

urlpatterns = [
    path('admin/', admin.site.urls),
    # Esta línea activa las funciones de Login y Logout
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('core.urls')),
    
    # URLs principales
    path('', core_views.home_page, name='home'),
    path('buscar/', core_views.buscar_productos, name='buscar_productos'),
    path('producto/<int:producto_id>/', core_views.detalle_producto, name='detalle_producto'),
    path('comprar/<int:producto_id>/', core_views.procesar_compra, name='procesar_compra'),
    
    # URLs de seguimiento de pedidos
    path('mis-pedidos/', core_views.seguimiento_pedidos, name='seguimiento_pedidos'),
    path('pedido/<int:pedido_id>/', core_views.seguimiento_pedido, name='seguimiento_pedido'),
    
    # URLs de perfil y contacto
    path('perfil/', core_views.perfil_cliente, name='perfil_cliente'),
    path('contacto/', core_views.contacto, name='contacto'),
    
    # URLs para repartidores
    path('repartidor/', core_views.panel_repartidor, name='panel_repartidor'),
    path('repartidor/aceptar/<int:pedido_id>/', core_views.aceptar_pedido, name='aceptar_pedido'),
    
    # API endpoints
    path('api/geocodificar/', core_views.geocodificar_direccion, name='geocodificar_direccion'),
    path('api/ubicacion/', core_views.actualizar_ubicacion_repartidor, name='actualizar_ubicacion_repartidor'),

    path('registro/', core_views.select_signup, name='select_signup'),
    path('registro/cliente/', core_views.cliente_signup, name='cliente_signup'),
    path('registro/farmacia/', core_views.farmacia_signup, name='farmacia_signup'),
    path('registro/repartidor/', core_views.repartidor_signup, name='repartidor_signup'),
]
