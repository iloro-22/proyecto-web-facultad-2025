from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from core import views as core_views
from core.auth_views import CustomLoginView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Login/logout personalizados
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    path('accounts/logout/', LogoutView.as_view(next_page='home'), name='logout'),

    # URLs de auth de Django
    path('accounts/', include('django.contrib.auth.urls')),

    # Rutas de la app core
    path('', include('core.urls')),

    # Rutas específicas de farmacia
    path('farmacia/', core_views.panel_farmacia, name='panel_farmacia'),
    path('farmacia/pedido/<int:pedido_id>/', core_views.detalle_pedido_farmacia, name='detalle_pedido_farmacia'),
    path('farmacia/pedido/<int:pedido_id>/confirmar-receta/', core_views.confirmar_receta_preparar, name='confirmar_receta_preparar'),
    path('farmacia/pedido/<int:pedido_id>/cancelar-receta/', core_views.cancelar_pedido_receta, name='cancelar_pedido_receta'),
    path('farmacia/pedido/<int:pedido_id>/entregar-repartidor/', core_views.entregar_al_repartidor, name='entregar_al_repartidor'),
    path('farmacia/pedido/<int:pedido_id>/listo-retiro/', core_views.listo_para_retiro, name='listo_para_retiro'),
    # Inventario se gestiona dentro del panel de farmacia (/farmacia/) en la pestaña correspondiente
    path('farmacia/inventario/producto/<int:producto_id>/actualizar-stock/', core_views.actualizar_stock, name='actualizar_stock'),
    path('farmacia/precios/', core_views.configuracion_precios, name='configuracion_precios'),
    path('farmacia/cuenta/', core_views.configuracion_cuenta_farmacia, name='configuracion_cuenta_farmacia'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
