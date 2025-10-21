#!/usr/bin/env python
"""
Script de prueba para la interfaz del farmacéutico de FarmaDelivery
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FarmaDeliveryProject.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Farmacia, Direccion, Producto, Cliente, Pedido, EstadoPedido, MetodoPago, ObraSocial, DetallePedido, RecetaMedica
from django.utils import timezone
from datetime import timedelta

def crear_datos_prueba():
    """Crear datos de prueba para la interfaz del farmacéutico"""
    
    print("Creando datos de prueba para la interfaz del farmaceutico...")
    
    # Crear dirección de prueba
    direccion, created = Direccion.objects.get_or_create(
        calle="Av. Corrientes",
        numero="1234",
        ciudad="Buenos Aires",
        provincia="Buenos Aires",
        codigo_postal="1043",
        defaults={
            'pais': 'Argentina',
            'latitud': -34.6037,
            'longitud': -58.3816
        }
    )
    
    # Crear usuario farmacéutico con DNI como username
    dni_farmacia = '12345678'  # DNI del farmacéutico
    
    user_farmacia, created = User.objects.get_or_create(
        username=dni_farmacia,
        defaults={
            'first_name': 'Dr. Juan',
            'last_name': 'Perez',
            'email': 'farmacia@test.com'
        }
    )
    if created:
        user_farmacia.set_password('test123')
        user_farmacia.save()
        print("Usuario farmaceutico creado")
    
    # Crear farmacia
    farmacia, created = Farmacia.objects.get_or_create(
        user=user_farmacia,
        defaults={
            'nombre': 'Farmacia del Centro',
            'direccion': direccion,
            'matricula': 'FAR123456',
            'cuit': '20123456789',
            'telefono': '011-1234-5678',
            'email_contacto': 'info@farmaciadelcentro.com',
            'horario_apertura': '08:00',
            'horario_cierre': '20:00',
            'activa': True
        }
    )
    if created:
        print("Farmacia creada")
    
    # Crear obra social de prueba
    obra_social, created = ObraSocial.objects.get_or_create(
        nombre='OSDE',
        defaults={
            'plan': '210',
            'numero_afiliado': 'OSDE123456'
        }
    )
    if created:
        print("Obra social creada")
    
    # Crear productos de prueba
    productos_data = [
        {
            'nombre': 'Aspirina 500mg',
            'descripcion': 'Analgesico y antiinflamatorio',
            'precio_base': 150.00,
            'codigo_barras': '7891234567890',
            'categoria': 'Analgesicos',
            'laboratorio': 'Bayer',
            'requiere_receta': False,
            'stock_disponible': 50
        },
        {
            'nombre': 'Ibuprofeno 400mg',
            'descripcion': 'Antiinflamatorio no esteroideo',
            'precio_base': 200.00,
            'codigo_barras': '7891234567891',
            'categoria': 'Antiinflamatorios',
            'laboratorio': 'Pfizer',
            'requiere_receta': False,
            'stock_disponible': 3
        },
        {
            'nombre': 'Omeprazol 20mg',
            'descripcion': 'Inhibidor de la bomba de protones',
            'precio_base': 300.00,
            'codigo_barras': '7891234567892',
            'categoria': 'Gastrointestinales',
            'laboratorio': 'AstraZeneca',
            'requiere_receta': True,
            'stock_disponible': 0
        },
        {
            'nombre': 'Paracetamol 500mg',
            'descripcion': 'Analgesico y antipiretico',
            'precio_base': 120.00,
            'codigo_barras': '7891234567893',
            'categoria': 'Analgesicos',
            'laboratorio': 'GSK',
            'requiere_receta': False,
            'stock_disponible': 25
        },
        {
            'nombre': 'Amoxicilina 500mg',
            'descripcion': 'Antibiotico de amplio espectro',
            'precio_base': 250.00,
            'codigo_barras': '7891234567894',
            'categoria': 'Antibioticos',
            'laboratorio': 'Roche',
            'requiere_receta': True,
            'stock_disponible': 15
        },
        {
            'nombre': 'Vitamina C 1000mg',
            'descripcion': 'Suplemento vitaminico',
            'precio_base': 80.00,
            'codigo_barras': '7891234567895',
            'categoria': 'Vitaminas',
            'laboratorio': 'Bayer',
            'requiere_receta': False,
            'stock_disponible': 30
        }
    ]
    
    for producto_data in productos_data:
        producto, created = Producto.objects.get_or_create(
            nombre=producto_data['nombre'],
            farmacia=farmacia,
            defaults=producto_data
        )
        if created:
            print(f"Producto creado: {producto.nombre}")
    
    # Crear cliente de prueba
    dni_cliente = '87654321'  # DNI del cliente
    
    user_cliente, created = User.objects.get_or_create(
        username=dni_cliente,
        defaults={
            'first_name': 'Maria',
            'last_name': 'Gonzalez',
            'email': 'cliente@test.com'
        }
    )
    if created:
        user_cliente.set_password('test123')
        user_cliente.save()
        print("Usuario cliente creado")
    
    cliente, created = Cliente.objects.get_or_create(
        user=user_cliente,
        defaults={
            'dni': dni_cliente,
            'direccion': direccion,
            'obra_social': obra_social,
            'telefono': '011-9876-5432'
        }
    )
    if created:
        print("Cliente creado")
    
    # Crear pedidos de prueba
    pedidos_data = [
        {
            'numero_pedido': 'FD20250121001',
            'estado': EstadoPedido.PENDIENTE,
            'metodo_pago': MetodoPago.EFECTIVO,
            'subtotal': 150.00,
            'descuento_total': 0.00,
            'total': 150.00,
            'observaciones': 'Entregar en horario de tarde',
            'productos': ['Aspirina 500mg']  # Sin receta
        },
        {
            'numero_pedido': 'FD20250121002',
            'estado': EstadoPedido.PREPARANDO,
            'metodo_pago': MetodoPago.TARJETA_DEBITO,
            'subtotal': 200.00,
            'descuento_total': 20.00,
            'total': 180.00,
            'observaciones': 'Cliente con alergia a la aspirina',
            'productos': ['Ibuprofeno 400mg']  # Sin receta
        },
        {
            'numero_pedido': 'FD20250121003',
            'estado': EstadoPedido.PENDIENTE,
            'metodo_pago': MetodoPago.MERCADO_PAGO,
            'subtotal': 300.00,
            'descuento_total': 0.00,
            'total': 300.00,
            'observaciones': 'Requiere receta medica',
            'productos': ['Omeprazol 20mg'],  # Con receta
            'tiene_receta': True
        },
        {
            'numero_pedido': 'FD20250121004',
            'estado': EstadoPedido.PENDIENTE,
            'metodo_pago': MetodoPago.TARJETA_CREDITO,
            'subtotal': 250.00,
            'descuento_total': 0.00,
            'total': 250.00,
            'observaciones': 'Antibiotico con receta',
            'productos': ['Amoxicilina 500mg'],  # Con receta
            'tiene_receta': True
        }
    ]
    
    for i, pedido_data in enumerate(pedidos_data):
        # Extraer productos y tiene_receta del diccionario
        productos_pedido = pedido_data.pop('productos', [])
        tiene_receta = pedido_data.pop('tiene_receta', False)
        
        pedido, created = Pedido.objects.get_or_create(
            numero_pedido=pedido_data['numero_pedido'],
            defaults={
                'cliente': cliente,
                'farmacia': farmacia,
                'direccion_entrega': direccion,
                'fecha_creacion': timezone.now() - timedelta(hours=i),
                'fecha_entrega_estimada': timezone.now() + timedelta(hours=2),
                **pedido_data
            }
        )
        if created:
            print(f"Pedido creado: {pedido.numero_pedido}")
            
            # Crear detalles del pedido
            for nombre_producto in productos_pedido:
                producto = Producto.objects.get(nombre=nombre_producto, farmacia=farmacia)
                DetallePedido.objects.create(
                    pedido=pedido,
                    producto=producto,
                    cantidad=1,
                    precio_unitario=producto.precio_base,
                    descuento_aplicado=0,
                    subtotal=producto.precio_base
                )
            
            # Crear receta médica si es necesario
            if tiene_receta:
                from core.models import RecetaMedica
                RecetaMedica.objects.create(
                    pedido=pedido,
                    observaciones_receta='Receta médica de prueba para demostración'
                )
                print(f"  - Receta médica creada para {pedido.numero_pedido}")
    
    print("\nDatos de prueba creados exitosamente!")
    print("\nInformacion de acceso:")
    print("   Farmaceutico:")
    print(f"   - Usuario: {dni_farmacia}")
    print("   - Contrasena: test123")
    print("   - URL: http://127.0.0.1:8000/farmacia/")
    print("\n   Cliente:")
    print(f"   - Usuario: {dni_cliente}")
    print("   - Contrasena: test123")
    print("   - URL: http://127.0.0.1:8000/")

def limpiar_datos_prueba():
    """Limpiar datos de prueba"""
    print("Limpiando datos de prueba...")
    
    # Eliminar pedidos
    Pedido.objects.filter(numero_pedido__startswith='FD20250121').delete()
    
    # Eliminar productos
    Producto.objects.filter(farmacia__nombre='Farmacia del Centro').delete()
    
    # Eliminar cliente
    Cliente.objects.filter(user__username='cliente_test').delete()
    User.objects.filter(username='cliente_test').delete()
    
    # Eliminar farmacia
    Farmacia.objects.filter(user__username='farmacia_test').delete()
    User.objects.filter(username='farmacia_test').delete()
    
    # Eliminar obra social
    ObraSocial.objects.filter(nombre='OSDE').delete()
    
    # Eliminar dirección
    Direccion.objects.filter(calle='Av. Corrientes', numero='1234').delete()
    
    print("Datos de prueba eliminados")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Gestionar datos de prueba para FarmaDelivery')
    parser.add_argument('--crear', action='store_true', help='Crear datos de prueba')
    parser.add_argument('--limpiar', action='store_true', help='Limpiar datos de prueba')
    
    args = parser.parse_args()
    
    if args.crear:
        crear_datos_prueba()
    elif args.limpiar:
        limpiar_datos_prueba()
    else:
        print("Uso: python crear_datos_prueba.py --crear o --limpiar")
        print("  --crear: Crear datos de prueba")
        print("  --limpiar: Limpiar datos de prueba")
