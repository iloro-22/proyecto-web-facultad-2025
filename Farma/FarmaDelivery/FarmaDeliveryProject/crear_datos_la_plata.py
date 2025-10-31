#!/usr/bin/env python
"""
Script para crear datos de prueba en La Plata para FarmaDelivery
- Limpia completamente la base de datos
- Crea 3 farmacias en direcciones específicas de La Plata
- Crea un cliente y un delivery
- Proporciona usuarios y contraseñas para testing
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
from core.models import Farmacia, Direccion, Producto, Cliente, Pedido, EstadoPedido, MetodoPago, ObraSocial, DetallePedido, RecetaMedica, Repartidor
from django.utils import timezone
from datetime import timedelta

def limpiar_base_datos():
    """Limpiar completamente la base de datos"""
    print("🧹 Limpiando completamente la base de datos...")
    
    # Eliminar todos los pedidos y detalles
    DetallePedido.objects.all().delete()
    Pedido.objects.all().delete()
    RecetaMedica.objects.all().delete()
    
    # Eliminar todos los productos
    Producto.objects.all().delete()
    
    # Eliminar clientes y repartidores
    Cliente.objects.all().delete()
    Repartidor.objects.all().delete()
    
    # Eliminar farmacias
    Farmacia.objects.all().delete()
    
    # Eliminar direcciones
    Direccion.objects.all().delete()
    
    # Eliminar obras sociales
    ObraSocial.objects.all().delete()
    
    # Eliminar usuarios (excepto superuser si existe)
    User.objects.filter(is_superuser=False).delete()
    
    print("✅ Base de datos limpiada completamente")

def crear_direcciones_la_plata():
    """Crear las direcciones específicas en La Plata"""
    direcciones = [
        {
            'calle': '1',
            'numero': '47-48',
            'ciudad': 'La Plata',
            'provincia': 'Buenos Aires',
            'codigo_postal': '1900',
            'pais': 'Argentina',
            'latitud': -34.9214,
            'longitud': -57.9544
        },
        {
            'calle': '5',
            'numero': '47-48',
            'ciudad': 'La Plata',
            'provincia': 'Buenos Aires',
            'codigo_postal': '1900',
            'pais': 'Argentina',
            'latitud': -34.9200,
            'longitud': -57.9500
        },
        {
            'calle': '140',
            'numero': '73-74',
            'ciudad': 'La Plata',
            'provincia': 'Buenos Aires',
            'codigo_postal': '1900',
            'pais': 'Argentina',
            'latitud': -34.9150,
            'longitud': -57.9400
        },
        {
            'calle': '1',
            'numero': '49-50',
            'ciudad': 'La Plata',
            'provincia': 'Buenos Aires',
            'codigo_postal': '1900',
            'pais': 'Argentina',
            'latitud': -34.9210,
            'longitud': -57.9540
        },
        {
            'calle': '3',
            'numero': '45-46',
            'ciudad': 'La Plata',
            'provincia': 'Buenos Aires',
            'codigo_postal': '1900',
            'pais': 'Argentina',
            'latitud': -34.9205,
            'longitud': -57.9520
        }
    ]
    
    direcciones_creadas = []
    for direccion_data in direcciones:
        direccion = Direccion.objects.create(**direccion_data)
        direcciones_creadas.append(direccion)
        print(f"📍 Dirección creada: {direccion.calle} {direccion.numero}, {direccion.ciudad}")
    
    return direcciones_creadas

def crear_farmacias(direcciones):
    """Crear las 3 farmacias en La Plata"""
    farmacias_data = [
        {
            'nombre': 'Farmacia Central',
            'direccion': direcciones[0],  # 1 entre 47 y 48
            'matricula': 'FAR001',
            'cuit': '20111111111',
            'telefono': '0221-111-1111',
            'email_contacto': 'central@farmacia.com',
            'horario_apertura': '08:00',
            'horario_cierre': '22:00',
            'activa': True,
            'dni': '11111111',
            'password': 'farmacia123',
            'first_name': 'Dr. Carlos',
            'last_name': 'Rodriguez'
        },
        {
            'nombre': 'Farmacia del Sol',
            'direccion': direcciones[1],  # 5 entre 47 y 48
            'matricula': 'FAR002',
            'cuit': '20222222222',
            'telefono': '0221-222-2222',
            'email_contacto': 'delsol@farmacia.com',
            'horario_apertura': '07:00',
            'horario_cierre': '23:00',
            'activa': True,
            'dni': '22222222',
            'password': 'farmacia123',
            'first_name': 'Dra. Ana',
            'last_name': 'Martinez'
        },
        {
            'nombre': 'Farmacia San Martín',
            'direccion': direcciones[2],  # 140 entre 73 y 74
            'matricula': 'FAR003',
            'cuit': '20333333333',
            'telefono': '0221-333-3333',
            'email_contacto': 'sanmartin@farmacia.com',
            'horario_apertura': '09:00',
            'horario_cierre': '21:00',
            'activa': True,
            'dni': '33333333',
            'password': 'farmacia123',
            'first_name': 'Dr. Luis',
            'last_name': 'Fernandez'
        }
    ]
    
    farmacias_creadas = []
    for farmacia_data in farmacias_data:
        # Crear usuario con DNI como username
        user = User.objects.create_user(
            username=farmacia_data['dni'],
            password=farmacia_data['password'],
            first_name=farmacia_data['first_name'],
            last_name=farmacia_data['last_name'],
            email=farmacia_data['email_contacto']
        )
        
        # Crear farmacia
        farmacia = Farmacia.objects.create(
            user=user,
            nombre=farmacia_data['nombre'],
            direccion=farmacia_data['direccion'],
            matricula=farmacia_data['matricula'],
            cuit=farmacia_data['cuit'],
            telefono=farmacia_data['telefono'],
            email_contacto=farmacia_data['email_contacto'],
            horario_apertura=farmacia_data['horario_apertura'],
            horario_cierre=farmacia_data['horario_cierre'],
            activa=farmacia_data['activa']
        )
        
        farmacias_creadas.append(farmacia)
        print(f"🏥 Farmacia creada: {farmacia.nombre} - Usuario: {farmacia_data['dni']}")
    
    return farmacias_creadas

def crear_productos_para_farmacias(farmacias):
    """Crear productos para cada farmacia"""
    productos_base = [
        {
            'nombre': 'Aspirina 500mg',
            'descripcion': 'Analgésico y antiinflamatorio',
            'precio_base': 150.00,
            'categoria': 'Analgésicos',
            'laboratorio': 'Bayer',
            'requiere_receta': False,
            'stock_disponible': 50
        },
        {
            'nombre': 'Ibuprofeno 400mg',
            'descripcion': 'Antiinflamatorio no esteroideo',
            'precio_base': 200.00,
            'categoria': 'Antiinflamatorios',
            'laboratorio': 'Pfizer',
            'requiere_receta': False,
            'stock_disponible': 30
        },
        {
            'nombre': 'Paracetamol 500mg',
            'descripcion': 'Analgésico y antipirético',
            'precio_base': 120.00,
            'categoria': 'Analgésicos',
            'laboratorio': 'GSK',
            'requiere_receta': False,
            'stock_disponible': 40
        },
        {
            'nombre': 'Omeprazol 20mg',
            'descripcion': 'Inhibidor de la bomba de protones',
            'precio_base': 300.00,
            'categoria': 'Gastrointestinales',
            'laboratorio': 'AstraZeneca',
            'requiere_receta': True,
            'stock_disponible': 25
        },
        {
            'nombre': 'Amoxicilina 500mg',
            'descripcion': 'Antibiótico de amplio espectro',
            'precio_base': 250.00,
            'categoria': 'Antibióticos',
            'laboratorio': 'Roche',
            'requiere_receta': True,
            'stock_disponible': 20
        },
        {
            'nombre': 'Vitamina C 1000mg',
            'descripcion': 'Suplemento vitamínico',
            'precio_base': 80.00,
            'categoria': 'Vitaminas',
            'laboratorio': 'Bayer',
            'requiere_receta': False,
            'stock_disponible': 35
        },
        {
            'nombre': 'Diclofenac 50mg',
            'descripcion': 'Antiinflamatorio y analgésico',
            'precio_base': 180.00,
            'categoria': 'Antiinflamatorios',
            'laboratorio': 'Novartis',
            'requiere_receta': False,
            'stock_disponible': 28
        },
        {
            'nombre': 'Loratadina 10mg',
            'descripcion': 'Antihistamínico para alergias',
            'precio_base': 90.00,
            'categoria': 'Antialérgicos',
            'laboratorio': 'Schering',
            'requiere_receta': False,
            'stock_disponible': 32
        },
        {
            'nombre': 'Metformina 500mg',
            'descripcion': 'Antidiabético oral',
            'precio_base': 220.00,
            'categoria': 'Antidiabéticos',
            'laboratorio': 'Merck',
            'requiere_receta': True,
            'stock_disponible': 15
        },
        {
            'nombre': 'Losartan 50mg',
            'descripcion': 'Antihipertensivo',
            'precio_base': 280.00,
            'categoria': 'Cardiovasculares',
            'laboratorio': 'MSD',
            'requiere_receta': True,
            'stock_disponible': 12
        }
    ]
    
    # Medicamentos con receta exclusivos para Farmacia Central
    medicamentos_receta_central = [
        {
            'nombre': 'Atorvastatina 20mg',
            'descripcion': 'Estatina para reducir el colesterol',
            'precio_base': 450.00,
            'categoria': 'Cardiovasculares',
            'laboratorio': 'Pfizer',
            'requiere_receta': True,
            'stock_disponible': 30
        },
        {
            'nombre': 'Enalapril 10mg',
            'descripcion': 'Inhibidor ECA para hipertensión',
            'precio_base': 320.00,
            'categoria': 'Cardiovasculares',
            'laboratorio': 'Merck',
            'requiere_receta': True,
            'stock_disponible': 25
        },
        {
            'nombre': 'Levotiroxina 100mcg',
            'descripcion': 'Hormona tiroidea sintética',
            'precio_base': 380.00,
            'categoria': 'Endocrinología',
            'laboratorio': 'Abbott',
            'requiere_receta': True,
            'stock_disponible': 20
        },
        {
            'nombre': 'Clonazepam 2mg',
            'descripcion': 'Ansiolítico y anticonvulsivante',
            'precio_base': 420.00,
            'categoria': 'Psicotrópicos',
            'laboratorio': 'Roche',
            'requiere_receta': True,
            'stock_disponible': 18
        },
        {
            'nombre': 'Sertralina 50mg',
            'descripcion': 'Antidepresivo ISRS',
            'precio_base': 520.00,
            'categoria': 'Psicotrópicos',
            'laboratorio': 'Pfizer',
            'requiere_receta': True,
            'stock_disponible': 22
        },
        {
            'nombre': 'Tramadol 50mg',
            'descripcion': 'Analgésico opioide',
            'precio_base': 480.00,
            'categoria': 'Analgésicos',
            'laboratorio': 'Grünenthal',
            'requiere_receta': True,
            'stock_disponible': 15
        },
        {
            'nombre': 'Alprazolam 0.5mg',
            'descripcion': 'Ansiolítico benzodiazepínico',
            'precio_base': 390.00,
            'categoria': 'Psicotrópicos',
            'laboratorio': 'Pfizer',
            'requiere_receta': True,
            'stock_disponible': 20
        },
        {
            'nombre': 'Prednisona 20mg',
            'descripcion': 'Corticosteroide antiinflamatorio',
            'precio_base': 350.00,
            'categoria': 'Corticosteroides',
            'laboratorio': 'Merck',
            'requiere_receta': True,
            'stock_disponible': 28
        },
        {
            'nombre': 'Salbutamol 100mcg Inhalador',
            'descripcion': 'Broncodilatador para asma',
            'precio_base': 550.00,
            'categoria': 'Respiratorios',
            'laboratorio': 'GSK',
            'requiere_receta': True,
            'stock_disponible': 24
        },
        {
            'nombre': 'Insulina Glargina 100UI/ml',
            'descripcion': 'Insulina de acción prolongada',
            'precio_base': 1200.00,
            'categoria': 'Antidiabéticos',
            'laboratorio': 'Sanofi',
            'requiere_receta': True,
            'stock_disponible': 12
        },
        {
            'nombre': 'Warfarina 5mg',
            'descripcion': 'Anticoagulante oral',
            'precio_base': 420.00,
            'categoria': 'Cardiovasculares',
            'laboratorio': 'Bristol-Myers',
            'requiere_receta': True,
            'stock_disponible': 16
        },
        {
            'nombre': 'Carbamazepina 200mg',
            'descripcion': 'Antiepiléptico',
            'precio_base': 380.00,
            'categoria': 'Neurología',
            'laboratorio': 'Novartis',
            'requiere_receta': True,
            'stock_disponible': 18
        }
    ]
    
    for i, farmacia in enumerate(farmacias, 1):
        print(f"📦 Agregando productos a {farmacia.nombre}...")
        productos_contador = 0
        
        # Agregar productos base a todas las farmacias
        for j, producto_data in enumerate(productos_base):
            # Variar precios ligeramente entre farmacias
            precio_variado = producto_data['precio_base'] + (hash(farmacia.nombre) % 50 - 25)
            stock_variado = producto_data['stock_disponible'] + (hash(farmacia.nombre) % 20 - 10)
            
            # Crear código de barras único para evitar conflictos
            codigo_barras = f"7891234567{i:03d}{j:03d}"
            
            Producto.objects.create(
                farmacia=farmacia,
                nombre=producto_data['nombre'],
                descripcion=producto_data['descripcion'],
                precio_base=max(precio_variado, 50),  # Precio mínimo $50
                codigo_barras=codigo_barras,
                categoria=producto_data['categoria'],
                laboratorio=producto_data['laboratorio'],
                requiere_receta=producto_data['requiere_receta'],
                stock_disponible=max(stock_variado, 5)  # Stock mínimo 5
            )
            productos_contador += 1
        
        # Agregar medicamentos con receta SOLO a Farmacia Central
        if farmacia.nombre == 'Farmacia Central':
            print(f"   💊 Agregando medicamentos con receta exclusivos a {farmacia.nombre}...")
            for k, medicamento_data in enumerate(medicamentos_receta_central):
                # Crear código de barras único para medicamentos con receta
                codigo_barras_receta = f"RX{i:03d}{k:04d}"
                
                Producto.objects.create(
                    farmacia=farmacia,
                    nombre=medicamento_data['nombre'],
                    descripcion=medicamento_data['descripcion'],
                    precio_base=medicamento_data['precio_base'],
                    codigo_barras=codigo_barras_receta,
                    categoria=medicamento_data['categoria'],
                    laboratorio=medicamento_data['laboratorio'],
                    requiere_receta=True,  # TODOS requieren receta
                    stock_disponible=medicamento_data['stock_disponible']
                )
                productos_contador += 1
            print(f"   ✅ {len(medicamentos_receta_central)} medicamentos con receta agregados")
        
        print(f"✅ {productos_contador} productos totales agregados a {farmacia.nombre}")

def crear_cliente(direcciones):
    """Crear cliente en 1 entre 49 y 50"""
    print("👤 Creando cliente...")
    
    # Crear usuario cliente con DNI como username
    user_cliente = User.objects.create_user(
        username='12345678',
        password='cliente123',
        first_name='María',
        last_name='González',
        email='maria.gonzalez@email.com'
    )
    
    # Crear obra social
    obra_social = ObraSocial.objects.create(
        nombre='OSDE',
        plan='210',
        numero_afiliado='OSDE123456'
    )
    
    # Crear cliente
    cliente = Cliente.objects.create(
        user=user_cliente,
        dni='12345678',
        direccion=direcciones[3],  # 1 entre 49 y 50
        obra_social=obra_social,
        telefono='0221-444-4444'
    )
    
    print(f"✅ Cliente creado: {cliente.user.first_name} {cliente.user.last_name}")
    print(f"   Usuario: {cliente.dni}")
    print(f"   Contraseña: cliente123")
    print(f"   Dirección: {cliente.direccion.calle} {cliente.direccion.numero}")
    
    return cliente

def crear_delivery(direcciones):
    """Crear delivery en 3 entre 45 y 46"""
    print("🚚 Creando delivery...")
    
    # Crear usuario delivery con DNI como username
    user_delivery = User.objects.create_user(
        username='87654321',
        password='delivery123',
        first_name='Juan',
        last_name='Pérez',
        email='juan.perez@delivery.com'
    )
    
    # Crear repartidor con ubicación fija para pruebas
    repartidor = Repartidor.objects.create(
        user=user_delivery,
        dni='87654321',
        telefono='0221-555-5555',
        tipo_vehiculo='MOTO',
        patente='ABC123',
        zona_cobertura='La Plata Centro',
        ubicacion_fija=True,  # Habilitar ubicación fija para pruebas
        latitud_fija=direcciones[4].latitud,  # 3 entre 45 y 46
        longitud_fija=direcciones[4].longitud,
        latitud_actual=direcciones[4].latitud,  # También configurar ubicación actual
        longitud_actual=direcciones[4].longitud,
        activo=True
    )
    
    print(f"✅ Delivery creado: {repartidor.user.first_name} {repartidor.user.last_name}")
    print(f"   Usuario: {repartidor.dni}")
    print(f"   Contraseña: delivery123")
    print(f"   Ubicación: {direcciones[4].calle} {direcciones[4].numero}")
    print(f"   Vehículo: {repartidor.get_tipo_vehiculo_display()} - Patente: {repartidor.patente}")
    
    return repartidor

def main():
    """Función principal para crear todos los datos"""
    print("🏥 FarmaDelivery - Creando datos de prueba en La Plata")
    print("=" * 60)
    
    # Limpiar base de datos
    limpiar_base_datos()
    
    # Crear direcciones
    direcciones = crear_direcciones_la_plata()
    
    # Crear farmacias
    farmacias = crear_farmacias(direcciones)
    
    # Crear productos para cada farmacia
    crear_productos_para_farmacias(farmacias)
    
    # Crear cliente
    cliente = crear_cliente(direcciones)
    
    # Crear delivery
    delivery = crear_delivery(direcciones)
    
    print("\n" + "=" * 60)
    print("🎉 DATOS CREADOS EXITOSAMENTE!")
    print("=" * 60)
    
    print("\n📋 INFORMACIÓN DE ACCESO:")
    print("\n🏥 FARMACIAS:")
    for i, farmacia in enumerate(farmacias, 1):
        print(f"   Farmacia {i}: {farmacia.nombre}")
        print(f"   - DNI (Usuario): {farmacia.user.username}")
        print(f"   - Contraseña: farmacia123")
        print(f"   - Dirección: {farmacia.direccion.calle} {farmacia.direccion.numero}")
        print(f"   - Teléfono: {farmacia.telefono}")
        print(f"   - Rol: FARMACIA")
        print()
    
    print("👤 CLIENTE:")
    print(f"   - DNI (Usuario): {cliente.user.username}")
    print(f"   - Contraseña: cliente123")
    print(f"   - Nombre: {cliente.user.first_name} {cliente.user.last_name}")
    print(f"   - Dirección: {cliente.direccion.calle} {cliente.direccion.numero}")
    print(f"   - Rol: CLIENTE")
    print()
    
    print("🚚 DELIVERY:")
    print(f"   - DNI (Usuario): {delivery.user.username}")
    print(f"   - Contraseña: delivery123")
    print(f"   - Nombre: {delivery.user.first_name} {delivery.user.last_name}")
    print(f"   - Ubicación: 3 45-46")
    print(f"   - Vehículo: {delivery.get_tipo_vehiculo_display()} - Patente: {delivery.patente}")
    print(f"   - Rol: REPARTIDOR")
    print()
    
    print("🌐 URLs PARA TESTING:")
    print("   - Cliente: http://127.0.0.1:8000/")
    print("   - Farmacias: http://127.0.0.1:8000/farmacia/")
    print("   - Delivery: http://127.0.0.1:8000/delivery/")
    print()
    
    print("📊 RESUMEN:")
    print(f"   - {len(farmacias)} farmacias creadas")
    print(f"   - {Producto.objects.count()} productos totales")
    print(f"   - 1 cliente creado")
    print(f"   - 1 delivery creado")
    print(f"   - {Direccion.objects.count()} direcciones en La Plata")

if __name__ == '__main__':
    main()
