from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth import login as auth_login
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from django.core.paginator import Paginator
import uuid
import os
from datetime import datetime, timedelta

from .models import (
    Cliente, Farmacia, Repartidor, Producto, Pedido, 
    DetallePedido, Direccion, ObraSocial, MetodoPago,
    EstadoPedido, DescuentoObraSocial, RecetaMedica,
    PedidoRechazado, # <--- asegurarse de importar el modelo
)
from .forms import (
    BusquedaProductoForm, RecetaForm, ConfirmacionPedidoForm,
    DireccionForm, PerfilClienteForm, ContactoForm,
    ClienteSignUpForm, FarmaciaSignUpForm, RepartidorSignUpForm
)

# Vista principal - página de inicio
@login_required 
def home_page(request):
    """Página principal con búsqueda de productos"""
    form = BusquedaProductoForm()
    
    # Obtener cliente actual para filtrar por distancia
    try:
        cliente = Cliente.objects.get(user=request.user)
        direccion_cliente = cliente.direccion
    except Cliente.DoesNotExist:
        direccion_cliente = None
    
    # Intentar completar coordenadas faltantes de la dirección del cliente
    if direccion_cliente and (not direccion_cliente.latitud or not direccion_cliente.longitud):
        try:
            import requests
            direccion_completa = f"{direccion_cliente.calle} {direccion_cliente.numero}, {direccion_cliente.ciudad}, {direccion_cliente.provincia}, Argentina"
            url = "https://nominatim.openstreetmap.org/search"
            params = {'q': direccion_completa, 'format': 'json', 'limit': 1, 'countrycodes': 'ar'}
            headers = {'User-Agent': 'FarmaDelivery/1.0'}
            r = requests.get(url, params=params, headers=headers, timeout=6)
            if r.status_code == 200 and r.json():
                lat = float(r.json()[0]['lat'])
                lon = float(r.json()[0]['lon'])
                direccion_cliente.latitud = lat
                direccion_cliente.longitud = lon
                direccion_cliente.save()
        except Exception:
            pass

    # Obtener productos destacados de farmacias cercanas
    productos_destacados = []
    if direccion_cliente and direccion_cliente.latitud and direccion_cliente.longitud:
        farmacias_cercanas = Farmacia.farmacias_cercanas(direccion_cliente, radio_km=2)
        farmacias_ids = [f['farmacia'].id for f in farmacias_cercanas]
        productos = Producto.objects.filter(activo=True, farmacia_id__in=farmacias_ids)[:6]
        
        for producto in productos:
            distancia = producto.farmacia.distancia_a_cliente(direccion_cliente)
            productos_destacados.append({
                'producto': producto,
                'distancia': round(distancia, 2) if distancia else None
            })
    else:
        # Si no hay dirección, mostrar productos aleatorios
        productos = Producto.objects.filter(activo=True)[:6]
        productos_destacados = [{'producto': p, 'distancia': None} for p in productos]
    
    context = {
        'form': form,
        'productos_destacados': productos_destacados,
        'direccion_cliente': direccion_cliente,
        'filtro_distancia': direccion_cliente and direccion_cliente.latitud and direccion_cliente.longitud,
    }
    return render(request, 'core/index.html', context)

# Vista de búsqueda de productos
@login_required
def buscar_productos(request):
    """Vista para buscar productos con filtros y geolocalización"""
    form = BusquedaProductoForm(request.GET)
    productos = Producto.objects.filter(activo=True)
    
    # Obtener cliente actual para filtrar por distancia
    try:
        cliente = Cliente.objects.get(user=request.user)
        direccion_cliente = cliente.direccion
    except Cliente.DoesNotExist:
        direccion_cliente = None
    
    if form.is_valid():
        busqueda = form.cleaned_data.get('busqueda')
        categoria = form.cleaned_data.get('categoria')
        farmacia = form.cleaned_data.get('farmacia')
        
        if busqueda:
            productos = productos.filter(nombre__icontains=busqueda)
        
        if categoria:
            if categoria == 'con_receta':
                productos = productos.filter(requiere_receta=True)
            elif categoria == 'venta_libre':
                productos = productos.filter(requiere_receta=False)
            else:
                productos = productos.filter(categoria__icontains=categoria)
            
        if farmacia:
            productos = productos.filter(farmacia=farmacia)
    
    # Intentar completar coordenadas faltantes de la dirección del cliente
    if direccion_cliente and (not direccion_cliente.latitud or not direccion_cliente.longitud):
        try:
            import requests
            direccion_completa = f"{direccion_cliente.calle} {direccion_cliente.numero}, {direccion_cliente.ciudad}, {direccion_cliente.provincia}, Argentina"
            url = "https://nominatim.openstreetmap.org/search"
            params = {'q': direccion_completa, 'format': 'json', 'limit': 1, 'countrycodes': 'ar'}
            headers = {'User-Agent': 'FarmaDelivery/1.0'}
            r = requests.get(url, params=params, headers=headers, timeout=6)
            if r.status_code == 200 and r.json():
                lat = float(r.json()[0]['lat'])
                lon = float(r.json()[0]['lon'])
                direccion_cliente.latitud = lat
                direccion_cliente.longitud = lon
                direccion_cliente.save()
        except Exception:
            pass

    # Filtrar productos por farmacias cercanas (2km) si el cliente tiene dirección
    productos_cercanos = []
    if direccion_cliente and direccion_cliente.latitud and direccion_cliente.longitud:
        farmacias_cercanas = Farmacia.farmacias_cercanas(direccion_cliente, radio_km=2)
        farmacias_ids = [f['farmacia'].id for f in farmacias_cercanas]
        productos = productos.filter(farmacia_id__in=farmacias_ids)
        
        # Agregar información de distancia a cada producto
        for producto in productos:
            distancia = producto.farmacia.distancia_a_cliente(direccion_cliente)
            productos_cercanos.append({
                'producto': producto,
                'distancia': round(distancia, 2) if distancia else None
            })
    else:
        # Si no hay dirección del cliente, mostrar todos los productos
        productos_cercanos = [{'producto': p, 'distancia': None} for p in productos]
    
    # Paginación
    paginator = Paginator(productos_cercanos, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'productos': page_obj,
        'total_resultados': len(productos_cercanos),
        'direccion_cliente': direccion_cliente,
        'aplico_cercania': bool(direccion_cliente and direccion_cliente.latitud and direccion_cliente.longitud),
        'tiene_direccion': bool(direccion_cliente),
    }
    return render(request, 'core/buscar_productos.html', context)

# Vista de detalle del producto
@login_required
def detalle_producto(request, producto_id):
    """Vista para ver detalles del producto y proceder a compra"""
    producto = get_object_or_404(Producto, id=producto_id, activo=True)
    
    # Obtener cliente actual
    try:
        cliente = Cliente.objects.get(user=request.user)
    except Cliente.DoesNotExist:
        messages.error(request, 'Debes completar tu perfil de cliente primero.')
        return redirect('perfil_cliente')
    
    # Calcular precio con descuento de obra social
    precio_final = producto.precio_base
    descuento_aplicado = 0
    
    if cliente.obra_social:
        try:
            descuento_obj = DescuentoObraSocial.objects.get(
                producto=producto,
                obra_social=cliente.obra_social,
                activo=True
            )
            if descuento_obj.descuento_porcentaje > 0:
                descuento_aplicado = (producto.precio_base * descuento_obj.descuento_porcentaje) / 100
            elif descuento_obj.descuento_fijo > 0:
                descuento_aplicado = descuento_obj.descuento_fijo
            
            precio_final = producto.precio_base - descuento_aplicado
        except DescuentoObraSocial.DoesNotExist:
            pass
    
    # Formularios - pasar la dirección del cliente para autocompletado si existe
    receta_form = RecetaForm(requiere_receta=producto.requiere_receta)
    direccion_form = DireccionForm(direccion_cliente=getattr(cliente, 'direccion', None))
    confirmacion_form = ConfirmacionPedidoForm()
    
    context = {
        'producto': producto,
        'cliente': cliente,
        'precio_final': precio_final,
        'descuento_aplicado': descuento_aplicado,
        'receta_form': receta_form,
        'direccion_form': direccion_form,
        'confirmacion_form': confirmacion_form,
        'requiere_receta': producto.requiere_receta,
    }
    return render(request, 'core/detalle_producto.html', context)

# Vista para procesar la compra
@login_required
@transaction.atomic
def procesar_compra(request, producto_id):
    """Vista para procesar la compra del producto"""
    if request.method != 'POST':
        return redirect('detalle_producto', producto_id=producto_id)
    
    producto = get_object_or_404(Producto, id=producto_id, activo=True)
    
    # Obtener cliente
    try:
        cliente = Cliente.objects.get(user=request.user)
    except Cliente.DoesNotExist:
        messages.error(request, 'Debes completar tu perfil de cliente primero.')
        return redirect('perfil_cliente')
    
    # Validar stock
    if producto.stock_disponible <= 0:
        messages.error(request, 'El producto no está disponible en este momento.')
        return redirect('detalle_producto', producto_id=producto_id)
    
    # Procesar formularios
    receta_form = RecetaForm(request.POST, request.FILES, requiere_receta=producto.requiere_receta)
    direccion_form = DireccionForm(request.POST)
    confirmacion_form = ConfirmacionPedidoForm(request.POST)
    
    if not (receta_form.is_valid() and direccion_form.is_valid() and confirmacion_form.is_valid()):
        messages.error(request, 'Por favor corrige los errores en el formulario.')
        return redirect('detalle_producto', producto_id=producto_id)
    
    # Validar que si el producto requiere receta, se haya subido un archivo
    if producto.requiere_receta and not receta_form.cleaned_data.get('archivo_receta'):
        messages.error(request, 'Este producto requiere receta médica. Por favor sube una foto o PDF de tu receta.')
        return redirect('detalle_producto', producto_id=producto_id)
    
    # Crear o obtener dirección
    direccion_data = direccion_form.cleaned_data
    latitud = request.POST.get('latitud')
    longitud = request.POST.get('longitud')
    
    direccion, created = Direccion.objects.get_or_create(
        calle=direccion_data['calle'],
        numero=direccion_data['numero'],
        ciudad=direccion_data['ciudad'],
        provincia=direccion_data['provincia'],
        codigo_postal=direccion_data['codigo_postal'],
        defaults={
            'pais': 'Argentina',
            'latitud': latitud if latitud else None,
            'longitud': longitud if longitud else None
        }
    )
    
    # Si la dirección ya existe pero no tiene coordenadas, actualizarlas
    if not created and not direccion.latitud and latitud:
        direccion.latitud = latitud
        direccion.longitud = longitud
        direccion.save()
    
    # Calcular precios
    precio_base = producto.precio_base
    descuento_aplicado = 0
    
    if cliente.obra_social:
        try:
            descuento_obj = DescuentoObraSocial.objects.get(
                producto=producto,
                obra_social=cliente.obra_social,
                activo=True
            )
            if descuento_obj.descuento_porcentaje > 0:
                descuento_aplicado = (precio_base * descuento_obj.descuento_porcentaje) / 100
            elif descuento_obj.descuento_fijo > 0:
                descuento_aplicado = descuento_obj.descuento_fijo
        except DescuentoObraSocial.DoesNotExist:
            pass
    
    precio_final = precio_base - descuento_aplicado
    
    # Crear pedido
    numero_pedido = f"FD{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
    
    pedido = Pedido.objects.create(
        cliente=cliente,
        farmacia=producto.farmacia,
        numero_pedido=numero_pedido,
        estado=EstadoPedido.PENDIENTE,
        metodo_pago=confirmacion_form.cleaned_data['metodo_pago'],
        subtotal=precio_base,
        descuento_total=descuento_aplicado,
        total=precio_final,
        direccion_entrega=direccion,
        observaciones=confirmacion_form.cleaned_data['observaciones'],
        fecha_entrega_estimada=timezone.now() + timedelta(hours=2)
    )
    
    # Crear detalle del pedido
    DetallePedido.objects.create(
        pedido=pedido,
        producto=producto,
        cantidad=1,
        precio_unitario=precio_base,
        descuento_aplicado=descuento_aplicado,
        subtotal=precio_final
    )
    
    # Reducir stock
    producto.stock_disponible -= 1
    producto.save()
    
    # Guardar receta si se subió
    if receta_form.cleaned_data.get('archivo_receta'):
        archivo_receta = receta_form.cleaned_data['archivo_receta']
        observaciones_receta = receta_form.cleaned_data.get('observaciones_receta', '')
        
        # Crear registro de receta médica
        RecetaMedica.objects.create(
            pedido=pedido,
            archivo_receta=archivo_receta,
            observaciones_receta=observaciones_receta
        )
    
    # Enviar email de confirmación
    enviar_email_confirmacion_pedido(pedido)
    
    messages.success(request, f'¡Pedido #{numero_pedido} creado exitosamente! Te enviaremos un email de confirmación.')
    return redirect('seguimiento_pedido', pedido_id=pedido.id)

# Vista de seguimiento de pedidos
@login_required
def seguimiento_pedidos(request):
    """Vista para ver todos los pedidos del cliente"""
    try:
        cliente = Cliente.objects.get(user=request.user)
    except Cliente.DoesNotExist:
        messages.error(request, 'Debes completar tu perfil de cliente primero.')
        return redirect('perfil_cliente')
    
    pedidos = Pedido.objects.filter(cliente=cliente).order_by('-fecha_creacion')
    
    # Paginación
    paginator = Paginator(pedidos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'pedidos': page_obj,
    }
    return render(request, 'core/seguimiento_pedidos.html', context)

# Vista de detalle de un pedido específico
@login_required
def seguimiento_pedido(request, pedido_id):
    """Vista para ver detalles de un pedido específico"""
    pedido = get_object_or_404(Pedido, id=pedido_id, cliente__user=request.user)
    
    context = {
        'pedido': pedido,
    }
    return render(request, 'core/seguimiento_pedido.html', context)

# Vista de perfil del cliente
@login_required
def perfil_cliente(request):
    """Vista para editar perfil del cliente"""
    try:
        cliente = Cliente.objects.get(user=request.user)
        pedidos_entregados_count = cliente.pedidos.filter(estado=EstadoPedido.ENTREGADO).count()
    except Cliente.DoesNotExist:
        # Crear cliente si no existe
        cliente = Cliente.objects.create(
            user=request.user,
            dni='00000000',  # Valor temporal
            direccion=Direccion.objects.first() or Direccion.objects.create(
                calle='Sin especificar',
                numero='0',
                ciudad='Sin especificar',
                provincia='Sin especificar',
                codigo_postal='0000'
            )
        )
        pedidos_entregados_count = 0
    
    if request.method == 'POST':
        form = PerfilClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('perfil_cliente')
    else:
        form = PerfilClienteForm(instance=cliente)
    
    context = {
        'cliente': cliente,
        'form': form,
        'pedidos_entregados_count': pedidos_entregados_count,
    }
    return render(request, 'core/perfil_cliente.html', context)

# Vista de contacto/soporte
def contacto(request):
    """Vista para formulario de contacto"""
    if request.method == 'POST':
        form = ContactoForm(request.POST)
        if form.is_valid():
            # Aquí podrías enviar el email
            messages.success(request, 'Mensaje enviado correctamente. Te responderemos pronto.')
            return redirect('contacto')
    else:
        form = ContactoForm()
    
    context = {
        'form': form,
    }
    return render(request, 'core/contacto.html', context)

# Vista para repartidores - panel de pedidos cercanos
@login_required
def panel_repartidor(request):
    """Panel para repartidores con pedidos cercanos"""
    try:
        repartidor = Repartidor.objects.get(user=request.user)
    except Repartidor.DoesNotExist:
        messages.error(request, 'No tienes permisos de repartidor.')
        return redirect('home')
    
    # Obtener pedidos cercanos
    pedidos_cercanos = repartidor.pedidos_cercanos(radio_km=2)
    
    context = {
        'repartidor': repartidor,
        'pedidos_cercanos': pedidos_cercanos,
        'esta_disponible': repartidor.esta_disponible(),
    }
    return render(request, 'core/panel_repartidor.html', context)

# Vista para actualizar ubicación del repartidor
@login_required
def actualizar_ubicacion_repartidor(request):
    """API endpoint para actualizar ubicación del repartidor"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        repartidor = Repartidor.objects.get(user=request.user)
    except Repartidor.DoesNotExist:
        return JsonResponse({'error': 'No tienes permisos de repartidor'}, status=403)
    
    try:
        latitud = float(request.POST.get('latitud'))
        longitud = float(request.POST.get('longitud'))
        
        repartidor.actualizar_ubicacion(latitud, longitud)
        
        return JsonResponse({
            'success': True,
            'mensaje': 'Ubicación actualizada correctamente',
            'pedidos_cercanos': len(repartidor.pedidos_cercanos())
        })
        
    except (ValueError, TypeError) as e:
        return JsonResponse({'error': 'Coordenadas inválidas'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Error interno: {str(e)}'}, status=500)

# API endpoint para obtener pedidos disponibles para repartidores
@login_required
def api_pedidos_disponibles(request):
    """API endpoint para obtener pedidos disponibles para repartidores"""
    try:
        repartidor = Repartidor.objects.get(user=request.user)
    except Repartidor.DoesNotExist:
        return JsonResponse({'error': 'No tienes permisos de repartidor'}, status=403)
    
    # Obtener pedidos cercanos
    pedidos_cercanos = repartidor.pedidos_cercanos_filtrado(radio_km=2)
    
    # Formatear datos para el frontend
    pedidos_data = []
    for pedido_info in pedidos_cercanos:
        pedido = pedido_info['pedido']
        distancia = pedido_info['distancia']
        
        # Calcular ganancia estimada (ejemplo: 15% del total)
        ganancia_estimada = float(pedido.total) * 0.15
        
        pedidos_data.append({
            'id': pedido.id,
            'numero': pedido.numero_pedido,
            'farmacia': pedido.farmacia.nombre,
            'direccion_farmacia': str(pedido.farmacia.direccion),
            'ganancia': round(ganancia_estimada, 2),
            'distancia': f"{distancia} km",
            'cliente': pedido.cliente.user.get_full_name(),
            'direccion_cliente': str(pedido.direccion_entrega),
            'productos': [detalle.producto.nombre for detalle in pedido.detalles.all()],
            'total': float(pedido.total),
            'fecha_creacion': pedido.fecha_creacion.strftime('%d/%m/%Y %H:%M')
        })
    
    return JsonResponse({
        'success': True,
        'pedidos': pedidos_data
    })

# API endpoint para obtener pedidos activos del repartidor autenticado
@login_required
def api_pedidos_activos(request):
    """Pedidos ya aceptados por el repartidor actual y en curso"""
    try:
        repartidor = Repartidor.objects.get(user=request.user)
    except Repartidor.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'No tienes permisos de repartidor'}, status=403)

    pedidos = Pedido.objects.filter(repartidor=repartidor, estado=EstadoPedido.EN_CAMINO).order_by('-fecha_creacion')

    data = []
    for pedido in pedidos:
        data.append({
            'id': pedido.id,
            'numero': pedido.numero_pedido,
            'farmacia': pedido.farmacia.nombre,
            'direccion_farmacia': str(pedido.farmacia.direccion),
            'cliente': pedido.cliente.user.get_full_name(),
            'direccion_cliente': str(pedido.direccion_entrega),
            'metodo_pago': pedido.metodo_pago,
            'monto_cobrar': float(pedido.total),
            'productos': [detalle.producto.nombre for detalle in pedido.detalles.all()],
            'estado': pedido.estado,
            'total': float(pedido.total),
        })

    return JsonResponse({'success': True, 'pedidos': data})

# Vista para aceptar un pedido
@login_required
def aceptar_pedido(request, pedido_id):
    """Vista para que un repartidor acepte un pedido"""
    try:
        repartidor = Repartidor.objects.get(user=request.user)
    except Repartidor.DoesNotExist:
        return JsonResponse({'error': 'No tienes permisos de repartidor'}, status=403)
    
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    # Verificar que el pedido esté disponible y cercano
    pedidos_cercanos = repartidor.pedidos_cercanos()
    pedido_cercano = None
    
    for item in pedidos_cercanos:
        if item['pedido'].id == pedido.id:
            pedido_cercano = item
            break
    
    if not pedido_cercano:
        return JsonResponse({'error': 'Pedido no disponible o fuera de alcance'}, status=400)
    
    # Asignar el pedido al repartidor
    pedido.repartidor = repartidor
    pedido.estado = EstadoPedido.EN_CAMINO
    pedido.save()
    
    # Enviar email de notificación
    enviar_email_cambio_estado(pedido, EstadoPedido.EN_CAMINO)
    
    return JsonResponse({
        'success': True,
        'message': f'Pedido #{pedido.numero_pedido} aceptado correctamente.',
        'pedido_id': pedido.id
    })

# Vista para rechazar un pedido
from django.views.decorators.http import require_POST
@require_POST
@login_required
def rechazar_pedido(request, pedido_id):
    """Permite al repartidor rechazar un pedido para no verlo más"""
    try:
        repartidor = Repartidor.objects.get(user=request.user)
    except Repartidor.DoesNotExist:
        return JsonResponse({'error': 'No tienes permisos de repartidor'}, status=403)
    pedido = get_object_or_404(Pedido, id=pedido_id)
    # Registrar rechazo si no existe
    PedidoRechazado.objects.get_or_create(pedido=pedido, repartidor=repartidor)
    return JsonResponse({'success': True, 'mensaje': 'Pedido rechazado'})

# Vista para geocodificar direcciones
def geocodificar_direccion(request):
    """API endpoint para geocodificar una dirección"""
    if request.method == 'POST':
        try:
            import requests
            
            calle = request.POST.get('calle')
            numero = request.POST.get('numero')
            ciudad = request.POST.get('ciudad')
            provincia = request.POST.get('provincia')
            
            if not all([calle, numero, ciudad, provincia]):
                return JsonResponse({'error': 'Faltan datos de la dirección'}, status=400)
            
            # Usar Nominatim (OpenStreetMap) para geocodificación gratuita
            direccion_completa = f"{calle} {numero}, {ciudad}, {provincia}, Argentina"
            url = f"https://nominatim.openstreetmap.org/search"
            params = {
                'q': direccion_completa,
                'format': 'json',
                'limit': 1,
                'countrycodes': 'ar'
            }
            headers = {
                'User-Agent': 'FarmaDelivery/1.0'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    lat = float(data[0]['lat'])
                    lon = float(data[0]['lon'])
                    return JsonResponse({
                        'latitud': lat,
                        'longitud': lon,
                        'direccion_encontrada': data[0]['display_name']
                    })
                else:
                    return JsonResponse({'error': 'Dirección no encontrada'}, status=404)
            else:
                return JsonResponse({'error': 'Error en el servicio de geocodificación'}, status=500)
                
        except Exception as e:
            return JsonResponse({'error': f'Error interno: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

# VISTAS PARA FARMACÉUTICOS

# Vista principal del panel farmacéutico
@login_required
def panel_farmacia(request):
    """Panel principal para farmacéuticos con gestión de pedidos, selección de pestaña activa, y visualización y edición completa de los productos."""
    try:
        farmacia = Farmacia.objects.get(user=request.user)
    except Farmacia.DoesNotExist:
        messages.error(request, 'No tienes permisos de farmacia.')
        return redirect('home')

    # Obtener pedidos de la farmacia
    pedidos_nuevos = Pedido.objects.filter(
        farmacia=farmacia,
        estado=EstadoPedido.PENDIENTE
    ).order_by('fecha_creacion')
    pedidos_preparando = Pedido.objects.filter(
        farmacia=farmacia,
        estado=EstadoPedido.PREPARANDO
    ).order_by('fecha_creacion')
    # Include both LISTO (waiting for driver) and EN_CAMINO (driver on the way)
    # so pharmacy can track orders until they're delivered
    pedidos_listos = Pedido.objects.filter(
        farmacia=farmacia,
        estado__in=[EstadoPedido.LISTO, EstadoPedido.EN_CAMINO]
    ).order_by('fecha_creacion')

    # Obtener productos del inventario (TODOS los de la farmacia, activos o no)
    productos = Producto.objects.filter(farmacia=farmacia).order_by('nombre')
    productos_sin_stock = productos.filter(stock_disponible=0)
    productos_poco_stock = productos.filter(stock_disponible__gt=0, stock_disponible__lte=5)
    productos_disponibles = productos.filter(stock_disponible__gt=5)

    # Determinar pestaña activa (GET o default)
    active_tab = request.GET.get('active_tab', 'pedidos')
    if active_tab not in ['pedidos','inventario','precios','cuenta']:
        active_tab = 'pedidos'

    context = {
        'farmacia': farmacia,
        'pedidos_nuevos': pedidos_nuevos,
        'pedidos_preparando': pedidos_preparando,
        'pedidos_listos': pedidos_listos,
        'productos_sin_stock': productos_sin_stock,
        'productos_poco_stock': productos_poco_stock,
        'productos_disponibles': productos_disponibles,
        'total_productos': productos.count(),
        'active_tab': active_tab,
    }
    return render(request, 'core/panel_farmacia.html', context)

# Vista para ver detalles de un pedido específico
@login_required
def detalle_pedido_farmacia(request, pedido_id):
    """Vista para ver detalles de un pedido específico en modal"""
    try:
        farmacia = Farmacia.objects.get(user=request.user)
    except Farmacia.DoesNotExist:
        return JsonResponse({'error': 'No tienes permisos de farmacia'}, status=403)
    
    pedido = get_object_or_404(Pedido, id=pedido_id, farmacia=farmacia)
    
    # Obtener detalles del pedido
    detalles = DetallePedido.objects.filter(pedido=pedido)
    
    # Obtener receta médica si existe
    receta = RecetaMedica.objects.filter(pedido=pedido).first()
    
    context = {
        'pedido': pedido,
        'detalles': detalles,
        'receta': receta,
    }
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Si es una petición AJAX, devolver solo el contenido del modal
        return render(request, 'core/modal_detalle_pedido.html', context)
    
    return render(request, 'core/detalle_pedido_farmacia.html', context)

# Vista para confirmar receta y preparar pedido
@login_required
def confirmar_receta_preparar(request, pedido_id):
    """Vista para confirmar receta y cambiar estado a preparando"""
    try:
        farmacia = Farmacia.objects.get(user=request.user)
    except Farmacia.DoesNotExist:
        return JsonResponse({'error': 'No tienes permisos de farmacia'}, status=403)
    
    pedido = get_object_or_404(Pedido, id=pedido_id, farmacia=farmacia)
    
    if pedido.estado != EstadoPedido.PENDIENTE:
        return JsonResponse({'error': 'El pedido no está en estado pendiente'}, status=400)
    
    # Cambiar estado a preparando
    pedido.estado = EstadoPedido.PREPARANDO
    pedido.save()
    
    # Marcar receta como validada si existe
    receta = RecetaMedica.objects.filter(pedido=pedido).first()
    if receta:
        from django.utils import timezone
        receta.validada_por_farmacia = True
        receta.fecha_validacion = timezone.now()
        receta.save()
    
    # Enviar email de notificación
    enviar_email_cambio_estado(pedido, EstadoPedido.PENDIENTE)
    
    return JsonResponse({
        'success': True,
        'mensaje': 'Receta confirmada y pedido en preparación',
        'nuevo_estado': pedido.get_estado_display()
    })

# Vista para cancelar pedido por receta inválida
@login_required
def cancelar_pedido_receta(request, pedido_id):
    """Vista para cancelar pedido por receta inválida"""
    try:
        farmacia = Farmacia.objects.get(user=request.user)
    except Farmacia.DoesNotExist:
        return JsonResponse({'error': 'No tienes permisos de farmacia'}, status=403)
    
    pedido = get_object_or_404(Pedido, id=pedido_id, farmacia=farmacia)
    
    if pedido.estado not in [EstadoPedido.PENDIENTE, EstadoPedido.PREPARANDO]:
        return JsonResponse({'error': 'No se puede cancelar este pedido'}, status=400)
    
    # Cambiar estado a cancelado
    pedido.estado = EstadoPedido.CANCELADO
    pedido.save()
    
    # Restaurar stock
    for detalle in pedido.detalles.all():
        producto = detalle.producto
        producto.stock_disponible += detalle.cantidad
        producto.save()
    
    # Enviar email de notificación
    enviar_email_cambio_estado(pedido, pedido.estado)
    
    return JsonResponse({
        'success': True,
        'mensaje': 'Pedido cancelado por receta inválida',
        'nuevo_estado': pedido.get_estado_display()
    })

# Vista para entregar pedido al repartidor
@login_required
def entregar_al_repartidor(request, pedido_id):
    """Vista para marcar pedido como entregado al repartidor"""
    try:
        farmacia = Farmacia.objects.get(user=request.user)
    except Farmacia.DoesNotExist:
        return JsonResponse({'error': 'No tienes permisos de farmacia'}, status=403)
    
    pedido = get_object_or_404(Pedido, id=pedido_id, farmacia=farmacia)
    
    if pedido.estado != EstadoPedido.PREPARANDO:
        return JsonResponse({'error': 'El pedido no está en preparación'}, status=400)
    
    # Cambiar estado a listo para entrega
    pedido.estado = EstadoPedido.LISTO
    pedido.save()
    
    # Enviar email de notificación
    enviar_email_cambio_estado(pedido, EstadoPedido.PREPARANDO)
    
    return JsonResponse({
        'success': True,
        'mensaje': 'Pedido entregado al repartidor',
        'nuevo_estado': pedido.get_estado_display()
    })

# Vista para marcar pedido como listo para retiro
@login_required
def listo_para_retiro(request, pedido_id):
    """Vista para marcar pedido como listo para retiro en farmacia"""
    try:
        farmacia = Farmacia.objects.get(user=request.user)
    except Farmacia.DoesNotExist:
        return JsonResponse({'error': 'No tienes permisos de farmacia'}, status=403)
    
    pedido = get_object_or_404(Pedido, id=pedido_id, farmacia=farmacia)
    
    if pedido.estado != EstadoPedido.PREPARANDO:
        return JsonResponse({'error': 'El pedido no está en preparación'}, status=400)
    
    # Cambiar estado a listo para retiro
    pedido.estado = EstadoPedido.LISTO
    pedido.save()
    
    # Enviar email de notificación
    enviar_email_cambio_estado(pedido, EstadoPedido.PREPARANDO)
    
    return JsonResponse({
        'success': True,
        'mensaje': 'Pedido listo para retiro',
        'nuevo_estado': pedido.get_estado_display()
    })

# Vista para entregar pedido al repartidor
@login_required
def entregar_pedido_repartidor(request, pedido_id):
    """El repartidor confirma una entrega. Cambia EN_CAMINO a ENTREGADO y retorna éxito"""
    try:
        repartidor = Repartidor.objects.get(user=request.user)
    except Repartidor.DoesNotExist:
        return JsonResponse({'error': 'No tienes permisos de repartidor'}, status=403)
    pedido = get_object_or_404(Pedido, id=pedido_id, repartidor=repartidor)
    if pedido.estado != EstadoPedido.EN_CAMINO:
        return JsonResponse({'error': 'Solo puedes confirmar entrega de pedidos en camino.'}, status=400)
    pedido.estado = EstadoPedido.ENTREGADO
    pedido.fecha_entrega_real = timezone.now()
    pedido.save()
    enviar_email_cambio_estado(pedido, EstadoPedido.EN_CAMINO)
    return JsonResponse({'success': True, 'mensaje': 'Pedido marcado como entregado.'})

# Vista para gestionar inventario
@login_required
def inventario_farmacia(request):
    """Vista para gestión de inventario de la farmacia"""
    try:
        farmacia = Farmacia.objects.get(user=request.user)
    except Farmacia.DoesNotExist:
        messages.error(request, 'No tienes permisos de farmacia.')
        return redirect('home')
    
    productos = Producto.objects.filter(farmacia=farmacia, activo=True).order_by('nombre')
    
    # Clasificar productos por estado de stock
    productos_sin_stock = productos.filter(stock_disponible=0)
    productos_poco_stock = productos.filter(stock_disponible__gt=0, stock_disponible__lte=5)
    productos_disponibles = productos.filter(stock_disponible__gt=5)
    
    context = {
        'farmacia': farmacia,
        'productos_sin_stock': productos_sin_stock,
        'productos_poco_stock': productos_poco_stock,
        'productos_disponibles': productos_disponibles,
        'total_productos': productos.count(),
    }
    return render(request, 'core/inventario_farmacia.html', context)

# Vista para actualizar stock de producto
@login_required
def actualizar_stock(request, producto_id):
    """Vista para actualizar stock de un producto"""
    try:
        farmacia = Farmacia.objects.get(user=request.user)
    except Farmacia.DoesNotExist:
        return JsonResponse({'error': 'No tienes permisos de farmacia'}, status=403)
    
    producto = get_object_or_404(Producto, id=producto_id, farmacia=farmacia)
    
    if request.method == 'POST':
        try:
            nuevo_stock = int(request.POST.get('stock'))
            if nuevo_stock < 0:
                return JsonResponse({'error': 'El stock no puede ser negativo'}, status=400)
            
            producto.stock_disponible = nuevo_stock
            producto.save()
            
            return JsonResponse({
                'success': True,
                'mensaje': f'Stock actualizado a {nuevo_stock} unidades',
                'nuevo_stock': nuevo_stock
            })
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Stock inválido'}, status=400)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

# Vista para configuración de precios y descuentos
@login_required
def configuracion_precios(request):
    """Vista para configurar precios y descuentos por obra social"""
    try:
        farmacia = Farmacia.objects.get(user=request.user)
    except Farmacia.DoesNotExist:
        messages.error(request, 'No tienes permisos de farmacia.')
        return redirect('home')
    
    productos = Producto.objects.filter(farmacia=farmacia, activo=True).order_by('nombre')
    obras_sociales = ObraSocial.objects.all().order_by('nombre')
    
    # Obtener descuentos existentes
    descuentos = DescuentoObraSocial.objects.filter(
        producto__farmacia=farmacia,
        activo=True
    ).select_related('producto', 'obra_social')
    
    context = {
        'farmacia': farmacia,
        'productos': productos,
        'obras_sociales': obras_sociales,
        'descuentos': descuentos,
    }
    return render(request, 'core/configuracion_precios.html', context)

# Vista para configuración de cuenta farmacia
@login_required
def configuracion_cuenta_farmacia(request):
    """Vista para configurar datos de la cuenta de farmacia"""
    try:
        farmacia = Farmacia.objects.get(user=request.user)
    except Farmacia.DoesNotExist:
        messages.error(request, 'No tienes permisos de farmacia.')
        return redirect('home')
    
    if request.method == 'POST':
        # Actualizar datos de la farmacia
        farmacia.nombre = request.POST.get('nombre', farmacia.nombre)
        farmacia.matricula = request.POST.get('matricula', farmacia.matricula)
        farmacia.cuit = request.POST.get('cuit', farmacia.cuit)
        farmacia.telefono = request.POST.get('telefono', farmacia.telefono)
        farmacia.email_contacto = request.POST.get('email_contacto', farmacia.email_contacto)
        farmacia.horario_apertura = request.POST.get('horario_apertura', farmacia.horario_apertura)
        farmacia.horario_cierre = request.POST.get('horario_cierre', farmacia.horario_cierre)
        
        # Actualizar dirección
        direccion = farmacia.direccion
        direccion.calle = request.POST.get('calle', direccion.calle)
        direccion.numero = request.POST.get('numero', direccion.numero)
        direccion.ciudad = request.POST.get('ciudad', direccion.ciudad)
        direccion.provincia = request.POST.get('provincia', direccion.provincia)
        direccion.codigo_postal = request.POST.get('codigo_postal', direccion.codigo_postal)
        direccion.save()
        
        farmacia.save()
        
        messages.success(request, 'Configuración actualizada correctamente.')
        return redirect('configuracion_cuenta_farmacia')
    
    context = {
        'farmacia': farmacia,
    }
    return render(request, 'core/configuracion_cuenta_farmacia.html', context)

# Funciones auxiliares
def enviar_email_confirmacion_pedido(pedido):
    """Envía email de confirmación del pedido"""
    try:
        subject = f'Confirmación de Pedido #{pedido.numero_pedido}'
        message = f"""
        Hola {pedido.cliente.user.get_full_name()},
        
        Tu pedido ha sido confirmado:
        
        Número de pedido: {pedido.numero_pedido}
        Farmacia: {pedido.farmacia.nombre}
        Total: ${pedido.total}
        Estado: {pedido.get_estado_display()}
        
        Te mantendremos informado sobre el estado de tu pedido.
        
        Gracias por elegirnos!
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [pedido.cliente.user.email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Error enviando email: {e}")

def enviar_email_cambio_estado(pedido, estado_anterior):
    """Envía email cuando cambia el estado del pedido"""
    try:
        subject = f'Actualización de Pedido #{pedido.numero_pedido}'
        message = f"""
        Hola {pedido.cliente.user.get_full_name()},
        
        El estado de tu pedido ha cambiado:
        
        Pedido: #{pedido.numero_pedido}
        Estado anterior: {dict(EstadoPedido.choices)[estado_anterior]}
        Estado actual: {pedido.get_estado_display()}
        
        """
        
        if pedido.estado == EstadoPedido.CANCELADO:
            message += "Tu pedido ha sido cancelado. Si tienes dudas, contáctanos."
        elif pedido.estado == EstadoPedido.ENTREGADO:
            message += "¡Tu pedido ha sido entregado! Gracias por elegirnos."
        elif pedido.estado == EstadoPedido.EN_CAMINO:
            message += "Tu pedido está en camino. El repartidor llegará pronto."
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [pedido.cliente.user.email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Error enviando email: {e}")


def select_signup(request):
    """Muestra la página para elegir qué tipo de usuario registrar."""
    return render(request, 'registration/select_signup.html')

def cliente_signup(request):
    """Maneja el registro de un nuevo Cliente."""
    if request.method == 'POST':
        form = ClienteSignUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Registro de cliente exitoso! Ahora podés iniciar sesión con tu DNI.')
            return redirect('login')
    else:
        form = ClienteSignUpForm()
    return render(request, 'registration/signup_form.html', {'form': form, 'user_type': 'Cliente'})

def farmacia_signup(request):
    """Maneja el registro de una nueva Farmacia."""
    if request.method == 'POST':
        form = FarmaciaSignUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.info(request, 'Solicitud de registro de farmacia enviada. Quedará pendiente de aprobación.')
            return redirect('login')
    else:
        form = FarmaciaSignUpForm()
    return render(request, 'registration/signup_form.html', {'form': form, 'user_type': 'Farmacia'})

def repartidor_signup(request):
    """Maneja el registro de un nuevo Repartidor."""
    if request.method == 'POST':
        form = RepartidorSignUpForm(request.POST, request.FILES)  # Importante: request.FILES
        if form.is_valid():
            form.save()
            messages.info(request, 'Solicitud de registro de repartidor enviada. Quedará pendiente de aprobación.')
            return redirect('login')
    else:
        form = RepartidorSignUpForm()
    return render(request, 'registration/signup_form.html', {'form': form, 'user_type': 'Repartidor'})
