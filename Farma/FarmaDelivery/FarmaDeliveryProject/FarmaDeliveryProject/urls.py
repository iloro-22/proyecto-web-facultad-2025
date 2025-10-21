# FarmaDeliveryProject/urls.py (Archivo principal del proyecto)

from django.contrib import admin
from django.urls import path, include
from core import views as core_views # Importamos la vista 'home_page' de tu app 'core'

urlpatterns = [
    path('admin/', admin.site.urls),
    # Esta línea activa las funciones de Login y Logout
    path('accounts/', include('django.contrib.auth.urls')),
    
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
    
    # URLs para farmacéuticos
    path('farmacia/', core_views.panel_farmacia, name='panel_farmacia'),
    path('farmacia/pedido/<int:pedido_id>/', core_views.detalle_pedido_farmacia, name='detalle_pedido_farmacia'),
    path('farmacia/pedido/<int:pedido_id>/confirmar-receta/', core_views.confirmar_receta_preparar, name='confirmar_receta_preparar'),
    path('farmacia/pedido/<int:pedido_id>/cancelar-receta/', core_views.cancelar_pedido_receta, name='cancelar_pedido_receta'),
    path('farmacia/pedido/<int:pedido_id>/entregar-repartidor/', core_views.entregar_al_repartidor, name='entregar_al_repartidor'),
    path('farmacia/pedido/<int:pedido_id>/listo-retiro/', core_views.listo_para_retiro, name='listo_para_retiro'),
    path('farmacia/inventario/', core_views.inventario_farmacia, name='inventario_farmacia'),
    path('farmacia/inventario/producto/<int:producto_id>/actualizar-stock/', core_views.actualizar_stock, name='actualizar_stock'),
    path('farmacia/precios/', core_views.configuracion_precios, name='configuracion_precios'),
    path('farmacia/cuenta/', core_views.configuracion_cuenta_farmacia, name='configuracion_cuenta_farmacia'),
    
    # API endpoints
    path('api/geocodificar/', core_views.geocodificar_direccion, name='geocodificar_direccion'),
    path('api/ubicacion/', core_views.actualizar_ubicacion_repartidor, name='actualizar_ubicacion_repartidor'),
]