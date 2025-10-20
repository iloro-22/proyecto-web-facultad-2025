#!/usr/bin/env python
"""
Script para crear datos de prueba para FarmaDelivery
Incluye farmacias reales de Buenos Aires con coordenadas precisas
"""

import os
import sys
import django
from datetime import datetime, time

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FarmaDeliveryProject.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import (
    Direccion, ObraSocial, Cliente, Farmacia, Repartidor, 
    Producto, DescuentoObraSocial, ListaProductos, 
    Pedido, DetallePedido, EstadoPedido, MetodoPago
)

def crear_direcciones():
    """Crear direcciones con coordenadas reales de Buenos Aires"""
    direcciones = [
        {
            'calle': 'Av. Corrientes',
            'numero': '1234',
            'ciudad': 'Buenos Aires',
            'provincia': 'Buenos Aires',
            'codigo_postal': '1043',
            'latitud': -34.6037,
            'longitud': -58.3816
        },
        {
            'calle': 'Av. Santa Fe',
            'numero': '2500',
            'ciudad': 'Buenos Aires',
            'provincia': 'Buenos Aires',
            'codigo_postal': '1425',
            'latitud': -34.5895,
            'longitud': -58.3974
        },
        {
            'calle': 'Av. Rivadavia',
            'numero': '4500',
            'ciudad': 'Buenos Aires',
            'provincia': 'Buenos Aires',
            'codigo_postal': '1406',
            'latitud': -34.6109,
            'longitud': -58.3960
        },
        {
            'calle': 'Av. Cabildo',
            'numero': '1800',
            'ciudad': 'Buenos Aires',
            'provincia': 'Buenos Aires',
            'codigo_postal': '1426',
            'latitud': -34.5700,
            'longitud': -58.4400
        },
        {
            'calle': 'Av. Cabildo',
            'numero': '2000',
            'ciudad': 'Buenos Aires',
            'provincia': 'Buenos Aires',
            'codigo_postal': '1426',
            'latitud': -34.5680,
            'longitud': -58.4420
        }
    ]
    
    direcciones_creadas = []
    for dir_data in direcciones:
        direccion, created = Direccion.objects.get_or_create(
            calle=dir_data['calle'],
            numero=dir_data['numero'],
            defaults=dir_data
        )
        direcciones_creadas.append(direccion)
        print(f"✓ Dirección creada: {direccion}")
    
    return direcciones_creadas

def crear_obras_sociales():
    """Crear obras sociales comunes en Argentina"""
    obras_sociales = [
        {
            'nombre': 'OSDE',
            'plan': '210',
            'numero_afiliado': 'OSDE210001'
        },
        {
            'nombre': 'Swiss Medical',
            'plan': 'SMG',
            'numero_afiliado': 'SMG001'
        },
        {
            'nombre': 'Galeno',
            'plan': 'Galeno 400',
            'numero_afiliado': 'GAL400001'
        },
        {
            'nombre': 'Medicus',
            'plan': 'Medicus 200',
            'numero_afiliado': 'MED200001'
        }
    ]
    
    obras_creadas = []
    for os_data in obras_sociales:
        obra_social, created = ObraSocial.objects.get_or_create(
            nombre=os_data['nombre'],
            defaults=os_data
        )
        obras_creadas.append(obra_social)
        print(f"✓ Obra Social creada: {obra_social}")
    
    return obras_creadas

def crear_farmacias(direcciones, obras_sociales):
    """Crear farmacias con datos reales"""
    farmacias_data = [
        {
            'nombre': 'Farmacia Central',
            'direccion': direcciones[0],
            'matricula': 'FAR001',
            'cuit': '20123456789',
            'telefono': '+54 11 4321-0001',
            'email_contacto': 'central@farmacia.com',
            'horario_apertura': time(8, 0),
            'horario_cierre': time(22, 0),
            'obras_sociales': obras_sociales[:2]  # OSDE y Swiss Medical
        },
        {
            'nombre': 'Farmacia del Pueblo',
            'direccion': direcciones[1],
            'matricula': 'FAR002',
            'cuit': '20987654321',
            'telefono': '+54 11 4321-0002',
            'email_contacto': 'pueblo@farmacia.com',
            'horario_apertura': time(7, 30),
            'horario_cierre': time(23, 0),
            'obras_sociales': obras_sociales[1:3]  # Swiss Medical y Galeno
        },
        {
            'nombre': 'Farmacia San Martín',
            'direccion': direcciones[2],
            'matricula': 'FAR003',
            'cuit': '20111222333',
            'telefono': '+54 11 4321-0003',
            'email_contacto': 'sanmartin@farmacia.com',
            'horario_apertura': time(9, 0),
            'horario_cierre': time(21, 0),
            'obras_sociales': obras_sociales[2:]  # Galeno y Medicus
        },
        {
            'nombre': 'Farmacia Belgrano',
            'direccion': direcciones[4],
            'matricula': 'FAR004',
            'cuit': '20444555666',
            'telefono': '+54 11 4321-0004',
            'email_contacto': 'belgrano@farmacia.com',
            'horario_apertura': time(8, 30),
            'horario_cierre': time(22, 30),
            'obras_sociales': obras_sociales[:2]  # OSDE y Swiss Medical
        }
    ]
    
    farmacias_creadas = []
    for farm_data in farmacias_data:
        # Crear usuario para la farmacia
        username = farm_data['nombre'].lower().replace(' ', '_')
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'first_name': farm_data['nombre'],
                'last_name': 'Farmacia',
                'email': farm_data['email_contacto']
            }
        )
        
        # Crear farmacia
        farmacia, created = Farmacia.objects.get_or_create(
            matricula=farm_data['matricula'],
            defaults={
                'user': user,
                'nombre': farm_data['nombre'],
                'direccion': farm_data['direccion'],
                'cuit': farm_data['cuit'],
                'telefono': farm_data['telefono'],
                'email_contacto': farm_data['email_contacto'],
                'horario_apertura': farm_data['horario_apertura'],
                'horario_cierre': farm_data['horario_cierre'],
                'activa': True
            }
        )
        
        # Agregar obras sociales
        farmacia.obras_sociales_aceptadas.set(farm_data['obras_sociales'])
        
        farmacias_creadas.append(farmacia)
        print(f"✓ Farmacia creada: {farmacia}")
    
    return farmacias_creadas

def crear_productos(farmacias):
    """Crear productos comunes de farmacia"""
    productos_data = [
        # Productos de venta libre
        {
            'nombre': 'Paracetamol 500mg',
            'descripcion': 'Analgésico y antipirético. Alivia el dolor y reduce la fiebre.',
            'precio_base': 950.00,
            'categoria': 'Analgésicos',
            'laboratorio': 'Bayer',
            'requiere_receta': False,
            'stock_disponible': 50,
            'codigo_barras': '7891234567890'
        },
        {
            'nombre': 'Ibuprofeno 400mg',
            'descripcion': 'Antiinflamatorio no esteroideo. Alivia dolor e inflamación.',
            'precio_base': 1200.00,
            'categoria': 'Antiinflamatorios',
            'laboratorio': 'Pfizer',
            'requiere_receta': False,
            'stock_disponible': 30,
            'codigo_barras': '7891234567891'
        },
        {
            'nombre': 'Omeprazol 20mg',
            'descripcion': 'Inhibidor de la bomba de protones. Protector gástrico.',
            'precio_base': 1550.00,
            'categoria': 'Digestivos',
            'laboratorio': 'AstraZeneca',
            'requiere_receta': False,
            'stock_disponible': 25,
            'codigo_barras': '7891234567892'
        },
        {
            'nombre': 'Loratadina 10mg',
            'descripcion': 'Antihistamínico. Alivia síntomas de alergia.',
            'precio_base': 890.00,
            'categoria': 'Antialérgicos',
            'laboratorio': 'Schering-Plough',
            'requiere_receta': False,
            'stock_disponible': 40,
            'codigo_barras': '7891234567893'
        },
        {
            'nombre': 'Aspirina 500mg',
            'descripcion': 'Ácido acetilsalicílico. Analgésico y antiinflamatorio.',
            'precio_base': 750.00,
            'categoria': 'Analgésicos',
            'laboratorio': 'Bayer',
            'requiere_receta': False,
            'stock_disponible': 35,
            'codigo_barras': '7891234567894'
        },
        # Productos con receta
        {
            'nombre': 'Amoxicilina 500mg',
            'descripcion': 'Antibiótico de amplio espectro.',
            'precio_base': 2500.00,
            'categoria': 'Antibióticos',
            'laboratorio': 'GlaxoSmithKline',
            'requiere_receta': True,
            'stock_disponible': 20,
            'codigo_barras': '7891234567895'
        },
        {
            'nombre': 'Losartán 50mg',
            'descripcion': 'Antihipertensivo. Bloqueador del receptor de angiotensina.',
            'precio_base': 3200.00,
            'categoria': 'Cardiovasculares',
            'laboratorio': 'Merck',
            'requiere_receta': True,
            'stock_disponible': 15,
            'codigo_barras': '7891234567896'
        },
        {
            'nombre': 'Metformina 850mg',
            'descripcion': 'Antidiabético oral. Controla los niveles de glucosa.',
            'precio_base': 1800.00,
            'categoria': 'Antidiabéticos',
            'laboratorio': 'Novartis',
            'requiere_receta': True,
            'stock_disponible': 18,
            'codigo_barras': '7891234567897'
        }
    ]
    
    productos_creados = []
    for farmacia in farmacias:
        for i, prod_data in enumerate(productos_data):
            # Generar código de barras único para cada farmacia
            codigo_base = prod_data['codigo_barras']
            codigo_farmacia = f"{codigo_base}{farmacia.id:02d}{i:02d}"
            
            producto, created = Producto.objects.get_or_create(
                nombre=prod_data['nombre'],
                farmacia=farmacia,
                defaults={
                    'descripcion': prod_data['descripcion'],
                    'precio_base': prod_data['precio_base'],
                    'categoria': prod_data['categoria'],
                    'laboratorio': prod_data['laboratorio'],
                    'requiere_receta': prod_data['requiere_receta'],
                    'stock_disponible': prod_data['stock_disponible'],
                    'codigo_barras': codigo_farmacia,
                    'activo': True
                }
            )
            productos_creados.append(producto)
            print(f"✓ Producto creado: {producto.nombre} en {farmacia.nombre}")
    
    return productos_creados

def crear_descuentos(productos, obras_sociales):
    """Crear descuentos por obra social"""
    descuentos_data = [
        # OSDE - descuentos altos
        {'obra_social': obras_sociales[0], 'descuento_porcentaje': 40.00, 'descuento_fijo': 0},
        # Swiss Medical - descuentos medios
        {'obra_social': obras_sociales[1], 'descuento_porcentaje': 30.00, 'descuento_fijo': 0},
        # Galeno - descuentos bajos
        {'obra_social': obras_sociales[2], 'descuento_porcentaje': 20.00, 'descuento_fijo': 0},
        # Medicus - descuentos fijos
        {'obra_social': obras_sociales[3], 'descuento_porcentaje': 0, 'descuento_fijo': 200.00}
    ]
    
    descuentos_creados = []
    for producto in productos:
        for desc_data in descuentos_data:
            descuento, created = DescuentoObraSocial.objects.get_or_create(
                producto=producto,
                obra_social=desc_data['obra_social'],
                defaults={
                    'descuento_porcentaje': desc_data['descuento_porcentaje'],
                    'descuento_fijo': desc_data['descuento_fijo'],
                    'activo': True
                }
            )
            descuentos_creados.append(descuento)
            print(f"✓ Descuento creado: {producto.nombre} - {desc_data['obra_social'].nombre}")
    
    return descuentos_creados

def crear_cliente_prueba(direcciones, obras_sociales):
    """Crear cliente de prueba con dirección cercana a las farmacias"""
    # Crear usuario cliente
    user, created = User.objects.get_or_create(
        username='cliente_prueba',
        defaults={
            'first_name': 'Juan',
            'last_name': 'Pérez',
            'email': 'juan.perez@email.com'
        }
    )
    
    if created:
        user.set_password('cliente123')
        user.save()
    
    # Crear cliente
    cliente, created = Cliente.objects.get_or_create(
        user=user,
        defaults={
            'dni': '12345678',
            'direccion': direcciones[3],  # Cabildo - más lejos para probar filtrado
            'obra_social': obras_sociales[0],  # OSDE
            'telefono': '+54 11 1234-5678',
            'fecha_nacimiento': datetime(1990, 5, 15).date()
        }
    )
    
    print(f"✓ Cliente creado: {cliente}")
    return cliente

def crear_repartidor_prueba():
    """Crear repartidor de prueba"""
    # Crear usuario repartidor
    user, created = User.objects.get_or_create(
        username='repartidor_prueba',
        defaults={
            'first_name': 'Carlos',
            'last_name': 'González',
            'email': 'carlos.gonzalez@email.com'
        }
    )
    
    if created:
        user.set_password('repartidor123')
        user.save()
    
    # Crear repartidor
    repartidor, created = Repartidor.objects.get_or_create(
        user=user,
        defaults={
            'dni': '87654321',
            'telefono': '+54 11 8765-4321',
            'vehiculo': 'Moto',
            'patente': 'ABC123',
            'zona_cobertura': 'Palermo, Recoleta, Belgrano',
            'activo': True
        }
    )
    
    print(f"✓ Repartidor creado: {repartidor}")
    return repartidor

def main():
    """Función principal para crear todos los datos de prueba"""
    print("🚀 Creando datos de prueba para FarmaDelivery...")
    print("=" * 50)
    
    # Crear direcciones
    print("\n📍 Creando direcciones...")
    direcciones = crear_direcciones()
    
    # Crear obras sociales
    print("\n🏥 Creando obras sociales...")
    obras_sociales = crear_obras_sociales()
    
    # Crear farmacias
    print("\n💊 Creando farmacias...")
    farmacias = crear_farmacias(direcciones, obras_sociales)
    
    # Crear productos
    print("\n💊 Creando productos...")
    productos = crear_productos(farmacias)
    
    # Crear descuentos
    print("\n💰 Creando descuentos...")
    descuentos = crear_descuentos(productos, obras_sociales)
    
    # Crear cliente de prueba
    print("\n👤 Creando cliente de prueba...")
    cliente = crear_cliente_prueba(direcciones, obras_sociales)
    
    # Crear repartidor de prueba
    print("\n🏍️ Creando repartidor de prueba...")
    repartidor = crear_repartidor_prueba()
    
    print("\n" + "=" * 50)
    print("✅ ¡Datos de prueba creados exitosamente!")
    print("\n📋 Resumen:")
    print(f"   • {len(direcciones)} direcciones")
    print(f"   • {len(obras_sociales)} obras sociales")
    print(f"   • {len(farmacias)} farmacias")
    print(f"   • {len(productos)} productos")
    print(f"   • {len(descuentos)} descuentos")
    print(f"   • 1 cliente de prueba")
    print(f"   • 1 repartidor de prueba")
    
    print("\n🔑 Credenciales de prueba:")
    print("   Cliente: usuario='cliente_prueba', password='cliente123'")
    print("   Repartidor: usuario='repartidor_prueba', password='repartidor123'")
    
    print("\n📍 Ubicaciones:")
    print("   • Farmacia Central: Av. Corrientes 1234 (Centro)")
    print("   • Farmacia del Pueblo: Av. Santa Fe 2500 (Palermo)")
    print("   • Farmacia San Martín: Av. Rivadavia 4500 (Caballito)")
    print("   • Cliente: Av. Cabildo 1800 (Belgrano) - más lejos para probar filtrado")

if __name__ == '__main__':
    main()
