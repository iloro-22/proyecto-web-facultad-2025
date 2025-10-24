<<<<<<< HEAD
# FarmaDeliveryProject/urls.py (Archivo principal del proyecto)

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView
from core import views as core_views # Importamos la vista 'home_page' de tu app 'core'
from core.auth_views import CustomLoginView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Login personalizado
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    path('accounts/logout/', LogoutView.as_view(next_page='home'), name='logout'),
    
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
    path('api/pedidos-disponibles/', core_views.api_pedidos_disponibles, name='api_pedidos_disponibles'),
]
=======
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from core import views as core_views
from core.auth_views import CustomLoginView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Login/logout personalizados (mantener)
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    path('accounts/logout/', LogoutView.as_view(next_page='home'), name='logout'),

    # Mantener las URLs de auth de Django (reset/password_change, etc.)
    path('accounts/', include('django.contrib.auth.urls')),

    # Incluir todas las rutas de la app core (home, buscar, mis-pedidos, perfil, api, etc.)
    path('', include('core.urls')),

    # Rutas específicas de farmacia que NO están en core/urls.py (únicas)
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
]

# Servir media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
>>>>>>> bf57f724a994412598a97a7cc751b19541788fa9
