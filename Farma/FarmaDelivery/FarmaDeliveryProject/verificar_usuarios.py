#!/usr/bin/env python
"""
Script para verificar usuarios creados y sus credenciales
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FarmaDeliveryProject.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Cliente

def verificar_usuarios():
    """Verificar usuarios creados"""
    print("🔍 Usuarios creados:")
    print("=" * 50)
    
    usuarios = User.objects.all()
    for user in usuarios:
        try:
            cliente = Cliente.objects.get(user=user)
            print(f"👤 Username: {user.username}")
            print(f"   Nombre: {user.get_full_name()}")
            print(f"   DNI: {cliente.dni}")
            print(f"   Email: {user.email}")
            print(f"   Password: cliente123")
            print("-" * 30)
        except Cliente.DoesNotExist:
            print(f"👤 Username: {user.username} (No es cliente)")
            print(f"   Nombre: {user.get_full_name()}")
            print(f"   Email: {user.email}")
            print("-" * 30)

if __name__ == '__main__':
    verificar_usuarios()

