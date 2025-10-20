from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator, RegexValidator

# Enumerativo de roles
class Rol(models.TextChoices):
    CLIENTE = 'CLIENTE', 'Cliente'
    FARMACIA = 'FARMACIA', 'Farmacia'
    REPARTIDOR = 'REPARTIDOR', 'Repartidor'
    ADMIN = 'ADMIN', 'Administrador'

# Modelo Direccion
class Direccion(models.Model):
    calle = models.CharField(max_length=100)
    numero = models.CharField(max_length=10)
    ciudad = models.CharField(max_length=50)
    provincia = models.CharField(max_length=50)
    codigo_postal = models.CharField(max_length=10)
    pais = models.CharField(max_length=50, default='Argentina')
    # Coordenadas geográficas
    latitud = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitud = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Dirección'
        verbose_name_plural = 'Direcciones'
    
    def __str__(self):
        return f"{self.calle} {self.numero}, {self.ciudad}, {self.provincia}"
    
    def calcular_distancia(self, otra_direccion):
        """Calcula la distancia en kilómetros entre dos direcciones usando la fórmula de Haversine"""
        if not (self.latitud and self.longitud and otra_direccion.latitud and otra_direccion.longitud):
            return None
        
        from math import radians, cos, sin, asin, sqrt
        
        # Convertir grados a radianes
        lat1, lon1 = radians(float(self.latitud)), radians(float(self.longitud))
        lat2, lon2 = radians(float(otra_direccion.latitud)), radians(float(otra_direccion.longitud))
        
        # Fórmula de Haversine
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        
        # Radio de la Tierra en kilómetros
        r = 6371
        return c * r

# Modelo ObraSocial
class ObraSocial(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    plan = models.CharField(max_length=100)
    numero_afiliado = models.CharField(max_length=50, unique=True)
    
    class Meta:
        verbose_name = 'Obra Social'
        verbose_name_plural = 'Obras Sociales'
    
    def __str__(self):
        return f"{self.nombre} - {self.plan}"

# Modelo Cliente
class Cliente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cliente')
    dni = models.CharField(
        max_length=8,
        unique=True,
        validators=[
            MinLengthValidator(7),
            RegexValidator(r'^\d+$', 'El DNI debe contener solo números')
        ]
    )
    direccion = models.ForeignKey(Direccion, on_delete=models.CASCADE)
    obra_social = models.ForeignKey(ObraSocial, on_delete=models.SET_NULL, null=True, blank=True)
    numero_afiliado = models.CharField(max_length=50, blank=True, null=True) # Campo específico del cliente
    telefono = models.CharField(max_length=20, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    rol = models.CharField(max_length=20, choices=Rol.choices, default=Rol.CLIENTE)
    
    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
    
    def __str__(self):
        return f"{self.user.get_full_name()} (DNI: {self.dni})"

# Modelo Farmacia
class Farmacia(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='farmacia')
    nombre = models.CharField(max_length=100)
    direccion = models.ForeignKey(Direccion, on_delete=models.CASCADE)
    matricula = models.CharField(max_length=20, unique=True)
    cuit = models.CharField(
        max_length=13,
        unique=True,
        validators=[
            MinLengthValidator(11),
            RegexValidator(r'^\d+$', 'El CUIT debe contener solo números')
        ]
    )
    obras_sociales_aceptadas = models.ManyToManyField(ObraSocial, blank=True, related_name='farmacias')
    telefono = models.CharField(max_length=20)
    email_contacto = models.EmailField()
    horario_apertura = models.TimeField()
    horario_cierre = models.TimeField()
    activa = models.BooleanField(default=True)
    rol = models.CharField(max_length=20, choices=Rol.choices, default=Rol.FARMACIA)
    
    class Meta:
        verbose_name = 'Farmacia'
        verbose_name_plural = 'Farmacias'
    
    def __str__(self):
        return f"{self.nombre} - {self.matricula}"
    
    @classmethod
    def farmacias_cercanas(cls, direccion_cliente, radio_km=2):
        """Retorna farmacias activas dentro del radio especificado"""
        farmacias_cercanas = []
        
        for farmacia in cls.objects.filter(activa=True):
            if farmacia.direccion.latitud and farmacia.direccion.longitud:
                distancia = farmacia.direccion.calcular_distancia(direccion_cliente)
                if distancia is not None and distancia <= radio_km:
                    farmacias_cercanas.append({
                        'farmacia': farmacia,
                        'distancia': round(distancia, 2)
                    })
        
        # Ordenar por distancia
        farmacias_cercanas.sort(key=lambda x: x['distancia'])
        return farmacias_cercanas
    
    def distancia_a_cliente(self, direccion_cliente):
        """Calcula la distancia de esta farmacia a un cliente"""
        return self.direccion.calcular_distancia(direccion_cliente)

# Modelo Repartidor
class Repartidor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='repartidor')
    dni = models.CharField(
        max_length=8,
        unique=True,
        validators=[
            MinLengthValidator(7),
            RegexValidator(r'^\d+$', 'El DNI debe contener solo números')
        ]
    )
    telefono = models.CharField(max_length=20)
    # ... dentro de class Repartidor(models.Model):

    # Tus campos para el vehículo
    TIPO_VEHICULO = [
        ('BICI', 'Bicicleta'),
        ('MOTO', 'Motocicleta'),
    ]

    tipo_vehiculo = models.CharField(max_length=10, choices=TIPO_VEHICULO, default='BICI')
    # El campo 'patente' ya existe en el modelo de los chicos, así que no lo repetimos.
    cedula_vehiculo = models.ImageField(upload_to='cedulas/', blank=True, null=True) # Tu campo de cédula
    patente = models.CharField(max_length=10, blank=True)
    activo = models.BooleanField(default=True)
    zona_cobertura = models.CharField(max_length=100, blank=True)
    # Ubicación en tiempo real
    latitud_actual = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitud_actual = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    ultima_actualizacion_ubicacion = models.DateTimeField(null=True, blank=True)
    rol = models.CharField(max_length=20, choices=Rol.choices, default=Rol.REPARTIDOR)
    
    class Meta:
        verbose_name = 'Repartidor'
        verbose_name_plural = 'Repartidores'
    
    def __str__(self):
        return f"{self.user.get_full_name()} (DNI: {self.dni})"
    
    def actualizar_ubicacion(self, latitud, longitud):
        """Actualiza la ubicación actual del repartidor"""
        from django.utils import timezone
        
        self.latitud_actual = latitud
        self.longitud_actual = longitud
        self.ultima_actualizacion_ubicacion = timezone.now()
        self.save()
    
    def pedidos_cercanos(self, radio_km=2):
        """Retorna pedidos cercanos al repartidor"""
        if not (self.latitud_actual and self.longitud_actual):
            return []
        
        # Crear una dirección temporal con la ubicación actual del repartidor
        ubicacion_actual = Direccion(
            latitud=self.latitud_actual,
            longitud=self.longitud_actual
        )
        
        pedidos_cercanos = []
        pedidos_disponibles = Pedido.objects.filter(
            estado__in=[EstadoPedido.LISTO, EstadoPedido.EN_CAMINO],
            repartidor__isnull=True
        )
        
        for pedido in pedidos_disponibles:
            if pedido.direccion_entrega.latitud and pedido.direccion_entrega.longitud:
                distancia = ubicacion_actual.calcular_distancia(pedido.direccion_entrega)
                if distancia is not None and distancia <= radio_km:
                    pedidos_cercanos.append({
                        'pedido': pedido,
                        'distancia': round(distancia, 2)
                    })
        
        # Ordenar por distancia
        pedidos_cercanos.sort(key=lambda x: x['distancia'])
        return pedidos_cercanos
    
    def esta_disponible(self):
        """Verifica si el repartidor está disponible (ubicación actualizada en los últimos 10 minutos)"""
        if not self.ultima_actualizacion_ubicacion:
            return False
        
        from django.utils import timezone
        from datetime import timedelta
        
        tiempo_limite = timezone.now() - timedelta(minutes=10)
        return self.ultima_actualizacion_ubicacion > tiempo_limite

# Modelo Producto
class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    precio_base = models.DecimalField(max_digits=10, decimal_places=2)
    codigo_barras = models.CharField(max_length=50, unique=True, blank=True)
    categoria = models.CharField(max_length=100, blank=True)
    laboratorio = models.CharField(max_length=100, blank=True)
    requiere_receta = models.BooleanField(default=False)
    stock_disponible = models.PositiveIntegerField(default=0)
    farmacia = models.ForeignKey(Farmacia, on_delete=models.CASCADE, related_name='productos')
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
    
    def __str__(self):
        return f"{self.nombre} - {self.farmacia.nombre}"

# Modelo DescuentoObraSocial
class DescuentoObraSocial(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='descuentos_obra_social')
    obra_social = models.ForeignKey(ObraSocial, on_delete=models.CASCADE)
    descuento_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    descuento_fijo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Descuento por Obra Social'
        verbose_name_plural = 'Descuentos por Obra Social'
        unique_together = ['producto', 'obra_social']
    
    def __str__(self):
        return f"{self.producto.nombre} - {self.obra_social.nombre} ({self.descuento_porcentaje}%)"

# Modelo ListaProductos
class ListaProductos(models.Model):
    nombre = models.CharField(max_length=100)
    productos = models.ManyToManyField(Producto, blank=True)
    farmacia = models.ForeignKey(Farmacia, on_delete=models.CASCADE, related_name='listas_productos')
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Lista de Productos'
        verbose_name_plural = 'Listas de Productos'
    
    def __str__(self):
        return f"{self.nombre} - {self.farmacia.nombre}"

# Enumerativo para estados de pedido
class EstadoPedido(models.TextChoices):
    PENDIENTE = 'PENDIENTE', 'Pendiente'
    CONFIRMADO = 'CONFIRMADO', 'Confirmado'
    PREPARANDO = 'PREPARANDO', 'Preparando'
    LISTO = 'LISTO', 'Listo para entrega'
    EN_CAMINO = 'EN_CAMINO', 'En camino'
    ENTREGADO = 'ENTREGADO', 'Entregado'
    CANCELADO = 'CANCELADO', 'Cancelado'

# Enumerativo para métodos de pago
class MetodoPago(models.TextChoices):
    EFECTIVO = 'EFECTIVO', 'Efectivo'
    TARJETA_DEBITO = 'TARJETA_DEBITO', 'Tarjeta de Débito'
    TARJETA_CREDITO = 'TARJETA_CREDITO', 'Tarjeta de Crédito'
    TRANSFERENCIA = 'TRANSFERENCIA', 'Transferencia Bancaria'
    MERCADO_PAGO = 'MERCADO_PAGO', 'Mercado Pago'

# Modelo Pedido
class Pedido(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='pedidos')
    farmacia = models.ForeignKey(Farmacia, on_delete=models.CASCADE, related_name='pedidos')
    repartidor = models.ForeignKey(Repartidor, on_delete=models.SET_NULL, null=True, blank=True, related_name='pedidos')
    numero_pedido = models.CharField(max_length=20, unique=True)
    estado = models.CharField(max_length=20, choices=EstadoPedido.choices, default=EstadoPedido.PENDIENTE)
    metodo_pago = models.CharField(max_length=20, choices=MetodoPago.choices)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    descuento_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    direccion_entrega = models.ForeignKey(Direccion, on_delete=models.CASCADE, related_name='pedidos_entrega')
    observaciones = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    fecha_entrega_estimada = models.DateTimeField(null=True, blank=True)
    fecha_entrega_real = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"Pedido #{self.numero_pedido} - {self.cliente.user.get_full_name()}"

# Modelo DetallePedido
class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    descuento_aplicado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = 'Detalle de Pedido'
        verbose_name_plural = 'Detalles de Pedido'
        unique_together = ['pedido', 'producto']
    
    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad} - Pedido #{self.pedido.numero_pedido}"
