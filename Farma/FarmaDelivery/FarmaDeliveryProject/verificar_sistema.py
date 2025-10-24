#!/usr/bin/env python
"""
Script para verificar que el sistema funcione correctamente
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

from core.models import Farmacia, Cliente, Repartidor, Producto, Pedido, EstadoPedido

def verificar_sistema():
    """Verificar que el sistema esté funcionando correctamente"""
    print("🔍 Verificando sistema FarmaDelivery...")
    print("=" * 50)
    
    # Verificar farmacias
    print("\n🏥 FARMACIAS:")
    farmacias = Farmacia.objects.all()
    for farmacia in farmacias:
        productos_count = Producto.objects.filter(farmacia=farmacia).count()
        print(f"  - {farmacia.nombre} (Usuario: {farmacia.user.username})")
        print(f"    Productos: {productos_count}")
        print(f"    Dirección: {farmacia.direccion}")
        print()
    
    # Verificar cliente
    print("👤 CLIENTE:")
    clientes = Cliente.objects.all()
    for cliente in clientes:
        print(f"  - {cliente.user.get_full_name()} (Usuario: {cliente.user.username})")
        print(f"    Dirección: {cliente.direccion}")
        print()
    
    # Verificar repartidor
    print("🚚 REPARTIDOR:")
    repartidores = Repartidor.objects.all()
    for repartidor in repartidores:
        print(f"  - {repartidor.user.get_full_name()} (Usuario: {repartidor.user.username})")
        print(f"    Ubicación fija: {repartidor.ubicacion_fija}")
        if repartidor.ubicacion_fija:
            print(f"    Latitud fija: {repartidor.latitud_fija}")
            print(f"    Longitud fija: {repartidor.longitud_fija}")
        print(f"    Vehículo: {repartidor.vehiculo}")
        print()
    
    # Verificar productos
    print("📦 PRODUCTOS:")
    productos = Producto.objects.all()
    print(f"  Total de productos: {productos.count()}")
    
    # Agrupar por farmacia
    for farmacia in farmacias:
        productos_farmacia = Producto.objects.filter(farmacia=farmacia)
        print(f"  - {farmacia.nombre}: {productos_farmacia.count()} productos")
        for producto in productos_farmacia[:3]:  # Mostrar solo los primeros 3
            print(f"    * {producto.nombre} - Stock: {producto.stock_disponible}")
        if productos_farmacia.count() > 3:
            print(f"    ... y {productos_farmacia.count() - 3} más")
        print()
    
    # Verificar pedidos
    print("📋 PEDIDOS:")
    pedidos = Pedido.objects.all()
    print(f"  Total de pedidos: {pedidos.count()}")
    
    for pedido in pedidos:
        print(f"  - Pedido #{pedido.numero_pedido}")
        print(f"    Cliente: {pedido.cliente.user.get_full_name()}")
        print(f"    Farmacia: {pedido.farmacia.nombre}")
        print(f"    Estado: {pedido.get_estado_display()}")
        print(f"    Total: ${pedido.total}")
        print()
    
    # Verificar pedidos cercanos al repartidor
    print("🎯 PEDIDOS CERCANOS AL REPARTIDOR:")
    if repartidores:
        repartidor = repartidores[0]
        pedidos_cercanos = repartidor.pedidos_cercanos(radio_km=2)
        print(f"  Pedidos cercanos a {repartidor.user.get_full_name()}: {len(pedidos_cercanos)}")
        
        for pedido_info in pedidos_cercanos:
            pedido = pedido_info['pedido']
            distancia = pedido_info['distancia']
            print(f"    - Pedido #{pedido.numero_pedido} - Distancia: {distancia} km")
            print(f"      Cliente: {pedido.cliente.user.get_full_name()}")
            print(f"      Farmacia: {pedido.farmacia.nombre}")
            print()
    
    print("✅ Verificación completada!")

if __name__ == '__main__':
    verificar_sistema()
