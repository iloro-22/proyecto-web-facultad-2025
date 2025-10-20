#!/usr/bin/env python
"""
Script para agregar farmacia cercana al cliente
"""

import os
import sys
import django
from datetime import time

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FarmaDeliveryProject.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Direccion, ObraSocial, Farmacia

def agregar_farmacia_cercana():
    """Agregar farmacia cerca del cliente"""
    
    # Crear dirección cercana al cliente
    direccion_cercana, created = Direccion.objects.get_or_create(
        calle='Av. Cabildo',
        numero='2000',
        defaults={
            'ciudad': 'Buenos Aires',
            'provincia': 'Buenos Aires',
            'codigo_postal': '1426',
            'latitud': -34.5680,
            'longitud': -58.4420
        }
    )
    
    if created:
        print(f"✓ Dirección creada: {direccion_cercana}")
    
    # Obtener obras sociales
    obras_sociales = ObraSocial.objects.all()[:2]  # OSDE y Swiss Medical
    
    # Crear usuario para la farmacia
    username = 'farmacia_belgrano'
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'first_name': 'Farmacia Belgrano',
            'last_name': 'Farmacia',
            'email': 'belgrano@farmacia.com'
        }
    )
    
    # Crear farmacia
    farmacia, created = Farmacia.objects.get_or_create(
        matricula='FAR004',
        defaults={
            'user': user,
            'nombre': 'Farmacia Belgrano',
            'direccion': direccion_cercana,
            'cuit': '20444555666',
            'telefono': '+54 11 4321-0004',
            'email_contacto': 'belgrano@farmacia.com',
            'horario_apertura': time(8, 30),
            'horario_cierre': time(22, 30),
            'activa': True
        }
    )
    
    # Agregar obras sociales
    farmacia.obras_sociales_aceptadas.set(obras_sociales)
    
    if created:
        print(f"✓ Farmacia creada: {farmacia}")
    else:
        print(f"✓ Farmacia ya existe: {farmacia}")
    
    # Crear productos para esta farmacia
    from core.models import Producto
    
    productos_data = [
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
        }
    ]
    
    for i, prod_data in enumerate(productos_data):
        codigo_farmacia = f"{prod_data['codigo_barras']}{farmacia.id:02d}{i:02d}"
        
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
        
        if created:
            print(f"✓ Producto creado: {producto.nombre} en {farmacia.nombre}")
    
    print("\n✅ ¡Farmacia cercana agregada exitosamente!")
    print(f"📍 Ubicación: {direccion_cercana}")
    print(f"📏 Distancia al cliente: ~0.3 km")

if __name__ == '__main__':
    agregar_farmacia_cercana()
