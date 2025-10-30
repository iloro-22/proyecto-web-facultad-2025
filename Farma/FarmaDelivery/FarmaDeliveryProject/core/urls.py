# core/urls.py
from django.urls import path
from . import views # Importa las vistas desde el directorio actual (core)

# app_name = 'core' # Opcional: define un namespace para las URLs de esta app

urlpatterns = [
    # URLs principales que ya tenías
    path('', views.home_page, name='home'),
    path('buscar/', views.buscar_productos, name='buscar_productos'),
    path('producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    path('comprar/<int:producto_id>/', views.procesar_compra, name='procesar_compra'),

    # URLs de seguimiento de pedidos
    path('mis-pedidos/', views.seguimiento_pedidos, name='seguimiento_pedidos'),
    path('pedido/<int:pedido_id>/', views.seguimiento_pedido, name='seguimiento_pedido'),

    # URLs de perfil y contacto
    path('perfil/', views.perfil_cliente, name='perfil_cliente'),
    path('contacto/', views.contacto, name='contacto'),

    # URLs para repartidores
    path('repartidor/', views.panel_repartidor, name='panel_repartidor'),
    path('repartidor/aceptar/<int:pedido_id>/', views.aceptar_pedido, name='aceptar_pedido'),
    path('repartidor/entregar/<int:pedido_id>/', views.entregar_pedido_repartidor, name='entregar_pedido_repartidor'),
    path('repartidor/rechazar/<int:pedido_id>/', views.rechazar_pedido, name='rechazar_pedido'),

    # URLs de Registro (movidas desde el urls.py principal)
    path('accounts/select_signup/', views.select_signup, name='select_signup'),
    path('accounts/signup/cliente/', views.cliente_signup, name='cliente_signup'),
    path('accounts/signup/farmacia/', views.farmacia_signup, name='farmacia_signup'),
    path('accounts/signup/repartidor/', views.repartidor_signup, name='repartidor_signup'),

    # API endpoints
    path('api/geocodificar/', views.geocodificar_direccion, name='geocodificar_direccion'),
    path('api/ubicacion/', views.actualizar_ubicacion_repartidor, name='actualizar_ubicacion_repartidor'),
    path('api/pedidos-disponibles/', views.api_pedidos_disponibles, name='api_pedidos_disponibles'),
    path('api/pedidos-activos/', views.api_pedidos_activos, name='api_pedidos_activos'),

    # Puedes añadir más URLs específicas de 'core' aquí
]