from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
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
    EstadoPedido, DescuentoObraSocial
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
            productos = productos.filter(categoria__icontains=categoria)
            
        if farmacia:
            productos = productos.filter(farmacia=farmacia)
    
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
        'filtro_distancia': direccion_cliente and direccion_cliente.latitud and direccion_cliente.longitud,
    }
    return render(request, 'core/buscar_productos.html', context)



def autocomplete_productos(request):
    """
    Vista para el autocompletado de productos.
    Busca productos cuyo nombre contenga el término proporcionado.
    """
    if 'term' in request.GET:
        term = request.GET.get('term').strip()
        
        # Validar que el término tenga al menos 2 caracteres
        if len(term) < 2:
            return JsonResponse([], safe=False)
        
        print(f"Buscando productos con término: '{term}'")  # Debug log
        
        # Empezamos el QuerySet base
        productos_qs = Producto.objects.filter(
            nombre__icontains=term,
            activo=True
        )

        print(f"Productos encontrados antes de filtros: {productos_qs.count()}")  # Debug log

        # --- Opcional: Filtrar por farmacias cercanas ANTES del slice ---
        try:
            # Asumiendo que el usuario está logueado y es un cliente
            cliente = Cliente.objects.get(user=request.user)
            direccion_cliente = cliente.direccion
            if direccion_cliente and direccion_cliente.latitud and direccion_cliente.longitud:
                farmacias_cercanas = Farmacia.farmacias_cercanas(direccion_cliente, radio_km=5) # Aumentamos el radio
                farmacias_ids = [f['farmacia'].id for f in farmacias_cercanas]
                print(f"Farmacias cercanas encontradas: {len(farmacias_ids)}")  # Debug log
                # Aplicamos el filtro AHORA
                productos_qs = productos_qs.filter(farmacia_id__in=farmacias_ids)
                print(f"Productos después de filtrar por cercanía: {productos_qs.count()}")  # Debug log
        except Cliente.DoesNotExist:
             # Si no es cliente o no tiene dirección, no filtramos por cercanía
             print("Usuario no es cliente o no tiene dirección")  # Debug log
             pass
        # --- Fin Opcional ---

        # Aplicamos values_list, distinct y el slice AL FINAL
        lista_nombres = list(
            productos_qs.values_list('nombre', flat=True).distinct()[:10]
        )
        
        print(f"Sugerencias finales: {lista_nombres}")  # Debug log
        return JsonResponse(lista_nombres, safe=False)

    return JsonResponse([], safe=False)

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
    
    # Formularios
    receta_form = RecetaForm()
    direccion_form = DireccionForm()
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
    receta_form = RecetaForm(request.POST, request.FILES)
    direccion_form = DireccionForm(request.POST)
    confirmacion_form = ConfirmacionPedidoForm(request.POST)
    
    if not (receta_form.is_valid() and direccion_form.is_valid() and confirmacion_form.is_valid()):
        messages.error(request, 'Por favor corrige los errores en el formulario.')
        return redirect('detalle_producto', producto_id=producto_id)
    
    # Validar receta si es requerida
    if producto.requiere_receta and not receta_form.cleaned_data.get('archivo_receta'):
        messages.error(request, 'Este producto requiere una receta médica.')
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
        # Aquí podrías guardar el archivo en el sistema de archivos
        # y asociarlo al pedido
        pass
    
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
        pass
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

# Vista para aceptar un pedido
@login_required
def aceptar_pedido(request, pedido_id):
    """Vista para que un repartidor acepte un pedido"""
    try:
        repartidor = Repartidor.objects.get(user=request.user)
    except Repartidor.DoesNotExist:
        messages.error(request, 'No tienes permisos de repartidor.')
        return redirect('home')
    
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    # Verificar que el pedido esté disponible y cercano
    pedidos_cercanos = repartidor.pedidos_cercanos()
    pedido_cercano = None
    
    for item in pedidos_cercanos:
        if item['pedido'].id == pedido.id:
            pedido_cercano = item
            break
    
    if not pedido_cercano:
        messages.error(request, 'Este pedido no está disponible o no está cerca de tu ubicación.')
        return redirect('panel_repartidor')
    
    # Asignar el pedido al repartidor
    pedido.repartidor = repartidor
    pedido.estado = EstadoPedido.EN_CAMINO
    pedido.save()
    
    # Enviar email de notificación
    enviar_email_cambio_estado(pedido, EstadoPedido.LISTO)
    
    messages.success(request, f'Pedido #{pedido.numero_pedido} aceptado correctamente.')
    return redirect('panel_repartidor')

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


# --- TUS VISTAS DE REGISTRO (AÑADIDAS AL FINAL) ---

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
        form = RepartidorSignUpForm(request.POST, request.FILES) # Importante: request.FILES
        if form.is_valid():
            form.save()
            messages.info(request, 'Solicitud de registro de repartidor enviada. Quedará pendiente de aprobación.')
            return redirect('login')
    else:
        form = RepartidorSignUpForm()
    return render(request, 'registration/signup_form.html', {'form': form, 'user_type': 'Repartidor'})