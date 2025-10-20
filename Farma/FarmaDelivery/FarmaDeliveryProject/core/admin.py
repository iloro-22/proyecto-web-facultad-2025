from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import (
    Direccion, ObraSocial, Cliente, Farmacia, Repartidor, 
    Producto, DescuentoObraSocial, ListaProductos, 
    Pedido, DetallePedido, Rol, EstadoPedido, MetodoPago
)

# Configuración inline para mostrar direcciones en otros modelos
class DireccionInline(admin.StackedInline):
    model = Direccion
    extra = 0

# Configuración del admin para Direccion
@admin.register(Direccion)
class DireccionAdmin(admin.ModelAdmin):
    list_display = ['calle', 'numero', 'ciudad', 'provincia', 'codigo_postal']
    list_filter = ['provincia', 'ciudad']
    search_fields = ['calle', 'ciudad', 'provincia']
    ordering = ['provincia', 'ciudad', 'calle']

# Configuración del admin para ObraSocial
@admin.register(ObraSocial)
class ObraSocialAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'plan', 'numero_afiliado']
    search_fields = ['nombre', 'plan', 'numero_afiliado']
    ordering = ['nombre']

# Configuración inline para mostrar clientes en User
class ClienteInline(admin.StackedInline):
    model = Cliente
    can_delete = False
    verbose_name_plural = 'Información de Cliente'
    fk_name = 'user'

# Configuración inline para mostrar farmacias en User
class FarmaciaInline(admin.StackedInline):
    model = Farmacia
    can_delete = False
    verbose_name_plural = 'Información de Farmacia'
    fk_name = 'user'

# Configuración inline para mostrar repartidores en User
class RepartidorInline(admin.StackedInline):
    model = Repartidor
    can_delete = False
    verbose_name_plural = 'Información de Repartidor'
    fk_name = 'user'

# Extender UserAdmin para incluir los perfiles
class CustomUserAdmin(UserAdmin):
    inlines = (ClienteInline, FarmaciaInline, RepartidorInline)
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)

# Re-registrar UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Configuración del admin para Cliente
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['user', 'dni', 'telefono', 'obra_social', 'rol']
    list_filter = ['rol', 'obra_social']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'dni']
    ordering = ['user__last_name', 'user__first_name']
    readonly_fields = ['rol']

# Configuración del admin para Farmacia
@admin.register(Farmacia)
class FarmaciaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'matricula', 'cuit', 'telefono', 'activa', 'rol']
    list_filter = ['activa', 'rol']
    search_fields = ['nombre', 'matricula', 'cuit', 'user__email']
    ordering = ['nombre']
    readonly_fields = ['rol']
    filter_horizontal = ['obras_sociales_aceptadas']

# Configuración del admin para Repartidor
@admin.register(Repartidor)
class RepartidorAdmin(admin.ModelAdmin):
    list_display = ['user', 'dni', 'telefono', 'vehiculo', 'activo', 'rol']
    list_filter = ['activo', 'rol', 'vehiculo']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'dni']
    ordering = ['user__last_name', 'user__first_name']
    readonly_fields = ['rol']

# Configuración inline para mostrar descuentos de obra social en productos
class DescuentoObraSocialInline(admin.TabularInline):
    model = DescuentoObraSocial
    extra = 0

# Configuración del admin para Producto
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'precio_base', 'stock_disponible', 'farmacia', 'categoria', 'activo']
    list_filter = ['activo', 'categoria', 'laboratorio', 'requiere_receta', 'farmacia']
    search_fields = ['nombre', 'descripcion', 'codigo_barras', 'categoria']
    ordering = ['nombre']
    inlines = [DescuentoObraSocialInline]

# Configuración del admin para DescuentoObraSocial
@admin.register(DescuentoObraSocial)
class DescuentoObraSocialAdmin(admin.ModelAdmin):
    list_display = ['producto', 'obra_social', 'descuento_porcentaje', 'descuento_fijo', 'activo']
    list_filter = ['activo', 'obra_social']
    search_fields = ['producto__nombre', 'obra_social__nombre']
    ordering = ['producto__nombre', 'obra_social__nombre']

# Configuración del admin para ListaProductos
@admin.register(ListaProductos)
class ListaProductosAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'farmacia', 'activa', 'fecha_creacion']
    list_filter = ['activa', 'farmacia']
    search_fields = ['nombre', 'farmacia__nombre']
    ordering = ['nombre']
    filter_horizontal = ['productos']

# Configuración inline para mostrar detalles de pedido
class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 0

# Configuración del admin para Pedido
@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ['numero_pedido', 'cliente', 'farmacia', 'estado', 'total', 'fecha_creacion']
    list_filter = ['estado', 'metodo_pago', 'farmacia', 'fecha_creacion']
    search_fields = ['numero_pedido', 'cliente__user__first_name', 'cliente__user__last_name']
    ordering = ['-fecha_creacion']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    inlines = [DetallePedidoInline]

# Configuración del admin para DetallePedido
@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ['pedido', 'producto', 'cantidad', 'precio_unitario', 'subtotal']
    list_filter = ['pedido__estado', 'pedido__farmacia']
    search_fields = ['pedido__numero_pedido', 'producto__nombre']
    ordering = ['pedido__fecha_creacion']
