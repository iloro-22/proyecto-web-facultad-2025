#!/usr/bin/env python
"""
Script para crear un repartidor de prueba para FarmaDelivery
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
from core.models import Repartidor, Direccion
from django.utils import timezone

def crear_repartidor_prueba():
    """Crear repartidor de prueba"""
    print("Creando repartidor de prueba...")
    
    # Crear usuario repartidor
    dni_repartidor = '11223344'  # DNI del repartidor
    
    user_repartidor, created = User.objects.get_or_create(
        username=dni_repartidor,
        defaults={
            'first_name': 'Carlos',
            'last_name': 'Rodriguez',
            'email': 'repartidor@test.com'
        }
    )
    if created:
        user_repartidor.set_password('test123')
        user_repartidor.save()
        print("Usuario repartidor creado")
    
    # Crear dirección del repartidor
    direccion_repartidor, created = Direccion.objects.get_or_create(
        calle='Av. Corrientes',
        numero='1234',
        ciudad='Buenos Aires',
        provincia='CABA',
        codigo_postal='1043',
        defaults={
            'latitud': -34.6037,
            'longitud': -58.3816
        }
    )
    
    # Crear repartidor
    repartidor, created = Repartidor.objects.get_or_create(
        user=user_repartidor,
        defaults={
            'dni': dni_repartidor,
            'telefono': '011-5555-6666',
            'vehiculo': 'MOTO',
            'patente': 'ABC123',
            'activo': True,
            'zona_cobertura': 'CABA y GBA'
        }
    )
    if created:
        print("Repartidor creado")
    
    print("\nRepartidor de prueba creado exitosamente!")
    print("\nInformacion de acceso:")
    print("   Repartidor:")
    print(f"   - Usuario: {dni_repartidor}")
    print("   - Contraseña: test123")
    print("   - URL: http://127.0.0.1:8000/repartidor/")

if __name__ == '__main__':
    crear_repartidor_prueba()
