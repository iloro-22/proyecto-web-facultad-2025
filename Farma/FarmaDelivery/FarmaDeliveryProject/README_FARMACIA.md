# 🏥 Interfaz del Farmacéutico - FarmaDelivery

## 📋 Descripción

Esta es la interfaz completa para farmacéuticos de la plataforma FarmaDelivery, diseñada con un estilo limpio, profesional y moderno centrado en la salud. Utiliza una paleta de colores dominada por tonos azules, blancos y verdes suaves, con diseño responsive y alta fidelidad visual.

## 🎨 Características del Diseño

- **Paleta de Colores**: Tonos azules, blancos y verdes suaves
- **Estilo**: Limpio, profesional, moderno y centrado en la salud
- **Responsive**: Adaptable a diferentes tamaños de pantalla
- **Usabilidad**: Enfocado en la claridad sobre la velocidad en el manejo de recetas

## 🚀 Funcionalidades Principales

### 1. Dashboard Principal (Pestaña 'Pedidos')
- **Ocupa 2/3 de la pantalla**
- **Secciones de estado**:
  - 'Pedidos Nuevos' - Pedidos pendientes de revisión
  - 'Pedidos en Preparación' - Pedidos confirmados en proceso

### 2. Visualización de Pedidos
- **Tarjetas rectangulares** con información clave:
  - ID del pedido
  - Nombre del cliente
  - Hora del pedido
  - Forma de pago
- **Interacción**: Click para ver detalles en modal

### 3. Modal de Detalle de Pedido
- **Lista de productos** con cantidad
- **Obra Social** del cliente
- **Receta Digital adjunta** (destacada para revisión)
- **Forma de Pago**
- **Dirección de entrega**

### 4. Botones de Acción
- **Confirmar Receta y Preparar**: Cambia estado a "Preparando Pedido"
- **Receta Inválida (Cancelar)**: Elimina el pedido de la lista activa
- **Entregado al Repartidor**: Para envíos a domicilio
- **Listo para Retirar**: Para retiros en farmacia

### 5. Gestión de Inventario (Pestaña 'Inventario')
- **Estados de Stock**:
  - 'Sin Stock' (rojo)
  - 'Poco Stock' (amarillo)
  - 'Disponible' (verde)
- **Actualización Manual**: El farmacéutico actualiza estados manualmente
- **Estadísticas**: Contadores por categoría de stock

### 6. Configuración de Precios (Pestaña 'Precios')
- **Lista de Obras Sociales** con descuentos asociados
- **Configuración de Descuentos**:
  - Descuento porcentual
  - Descuento fijo
- **Gestión por Producto**

### 7. Configuración de Cuenta (Pestaña 'Mi Cuenta')
- **Datos de la Farmacia**:
  - Nombre, DNI, CUIT, matrícula
  - Dirección completa
  - Horarios de atención
  - Información de contacto

## 🛠️ Instalación y Configuración

### 1. Requisitos
- Python 3.8+
- Django 5.2+
- Base de datos SQLite (desarrollo) o PostgreSQL (producción)

### 2. Instalación
```bash
# Clonar el repositorio
git clone <repository-url>
cd FarmaDeliveryProject

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser
```

### 3. Datos de Prueba
```bash
# Crear datos de prueba para farmacéutico
python crear_datos_prueba_farmacia.py --crear

# Limpiar datos de prueba
python crear_datos_prueba_farmacia.py --limpiar
```

### 4. Ejecutar Servidor
```bash
python manage.py runserver
```

## 🔐 Acceso a la Interfaz

### Usuario Farmacéutico de Prueba
- **URL**: `http://127.0.0.1:8000/farmacia/`
- **Usuario**: `farmacia_test`
- **Contraseña**: `test123`

### Usuario Cliente de Prueba
- **URL**: `http://127.0.0.1:8000/`
- **Usuario**: `cliente_test`
- **Contraseña**: `test123`

## 📁 Estructura de Archivos

```
FarmaDeliveryProject/
├── core/
│   ├── templates/core/
│   │   ├── panel_farmacia.html          # Template principal
│   │   └── modal_detalle_pedido.html   # Modal de detalles
│   ├── views.py                         # Vistas del farmacéutico
│   ├── forms.py                        # Formularios específicos
│   └── models.py                       # Modelos de datos
├── static/
│   ├── css/
│   │   └── farmacia.css                # Estilos principales
│   └── js/
│       └── farmacia.js                 # Funcionalidad JavaScript
├── FarmaDeliveryProject/
│   ├── urls.py                         # Configuración de URLs
│   └── settings.py                     # Configuración del proyecto
└── crear_datos_prueba_farmacia.py      # Script de datos de prueba
```

## 🎯 URLs Principales

- `/farmacia/` - Panel principal del farmacéutico
- `/farmacia/pedido/<id>/` - Detalle de pedido específico
- `/farmacia/pedido/<id>/confirmar-receta/` - Confirmar receta
- `/farmacia/pedido/<id>/cancelar-receta/` - Cancelar pedido
- `/farmacia/pedido/<id>/entregar-repartidor/` - Entregar al repartidor
- `/farmacia/pedido/<id>/listo-retiro/` - Listo para retiro
- `/farmacia/inventario/` - Gestión de inventario
- `/farmacia/precios/` - Configuración de precios
- `/farmacia/cuenta/` - Configuración de cuenta

## 🔄 Flujo de Trabajo

### 1. Pedidos Nuevos
1. Farmacéutico recibe notificación de nuevo pedido
2. Revisa detalles del pedido en modal
3. Verifica receta médica (si aplica)
4. Decide: Confirmar o Cancelar

### 2. Pedidos en Preparación
1. Pedido confirmado pasa a "Preparando"
2. Farmacéutico prepara medicamentos
3. Según tipo de entrega:
   - **Domicilio**: Marca como "Entregado al Repartidor"
   - **Retiro**: Marca como "Listo para Retirar"

### 3. Gestión de Inventario
1. Farmacéutico revisa estados de stock
2. Actualiza cantidades manualmente
3. Productos se reclasifican automáticamente según stock

## 🎨 Personalización de Estilos

### Variables CSS Principales
```css
:root {
    --primary-blue: #2563eb;
    --secondary-blue: #3b82f6;
    --success-green: #10b981;
    --warning-orange: #f59e0b;
    --danger-red: #ef4444;
}
```

### Clases de Estado
- `.sin-stock` - Productos sin stock (rojo)
- `.poco-stock` - Productos con poco stock (amarillo)
- `.disponible` - Productos disponibles (verde)
- `.preparando` - Pedidos en preparación (naranja)

## 📱 Responsive Design

- **Desktop**: Layout completo con sidebar y grid
- **Tablet**: Layout adaptado con navegación por pestañas
- **Mobile**: Layout vertical optimizado para pantallas pequeñas

## 🔧 Funcionalidades JavaScript

### Principales Funciones
- `showPedidoModal()` - Mostrar detalles del pedido
- `confirmarReceta()` - Confirmar receta y preparar
- `cancelarReceta()` - Cancelar pedido por receta inválida
- `actualizarStock()` - Actualizar stock de productos
- `showToast()` - Mostrar notificaciones

### Eventos Principales
- Click en tarjetas de pedidos
- Submit de formularios
- Cambio de pestañas
- Actualización de stock

## 🚨 Restricciones de Interacción

- **No se muestra información del repartidor** asignado
- **Descuento de stock es manual**, no vinculado a confirmación de receta
- **Prioridad en claridad** sobre velocidad en manejo de recetas

## 🐛 Solución de Problemas

### Problemas Comunes

1. **Archivos estáticos no cargan**
   ```bash
   python manage.py collectstatic
   ```

2. **Errores de migración**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Problemas de permisos**
   - Verificar que el usuario tenga rol de farmacia
   - Revisar configuración de autenticación

## 📞 Soporte

Para soporte técnico o consultas sobre la interfaz del farmacéutico, contactar al equipo de desarrollo.

---

**FarmaDelivery** - Plataforma de entrega de medicamentos a domicilio
