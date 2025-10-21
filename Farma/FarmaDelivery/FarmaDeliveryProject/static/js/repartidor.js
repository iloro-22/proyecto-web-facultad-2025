/* ===== PANEL REPARTIDOR - JAVASCRIPT ===== */

// Variables globales
let pedidosDisponibles = [];
let pedidosActivos = [];
let pedidoActivoActual = null;

// Inicialización cuando el DOM está listo
document.addEventListener('DOMContentLoaded', function() {
    console.log('Inicializando panel del repartidor...');
    
    // Inicializar componentes
    initTabs();
    initModal();
    initToast();
    initForms();
    
    // Cargar datos iniciales
    cargarPedidosDisponibles();
    cargarPedidosActivos();
    
    console.log('Panel del repartidor inicializado correctamente');
});

/* ===== FUNCIONALIDAD DE PESTAÑAS ===== */

function initTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetTab = this.getAttribute('data-tab');
            
            // Remover clase active de todos los botones y panes
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabPanes.forEach(pane => pane.classList.remove('active'));
            
            // Agregar clase active al botón y pane seleccionados
            this.classList.add('active');
            document.getElementById(targetTab).classList.add('active');
            
            // Cargar contenido específico de la pestaña
            if (targetTab === 'disponibles') {
                cargarPedidosDisponibles();
            } else if (targetTab === 'activos') {
                cargarPedidosActivos();
            }
        });
    });
}

/* ===== CARGA DE PEDIDOS DISPONIBLES ===== */

function cargarPedidosDisponibles() {
    console.log('Cargando pedidos disponibles...');
    
    // Simular datos de pedidos disponibles
    pedidosDisponibles = [
        {
            id: 1,
            numero: 'FD20250121001',
            farmacia: 'Farmacia del Centro',
            direccion_farmacia: 'Av. Corrientes 1234, CABA',
            ganancia: 450,
            distancia: '2.3 km',
            cliente: 'María González',
            direccion_cliente: 'Av. Santa Fe 5678, CABA',
            productos: ['Aspirina 500mg', 'Paracetamol 500mg'],
            total: 270
        },
        {
            id: 2,
            numero: 'FD20250121002',
            farmacia: 'Farmacia del Centro',
            direccion_farmacia: 'Av. Corrientes 1234, CABA',
            ganancia: 380,
            distancia: '1.8 km',
            cliente: 'Juan Pérez',
            direccion_cliente: 'Av. Córdoba 2345, CABA',
            productos: ['Ibuprofeno 400mg'],
            total: 200
        },
        {
            id: 3,
            numero: 'FD20250121003',
            farmacia: 'Farmacia del Centro',
            direccion_farmacia: 'Av. Corrientes 1234, CABA',
            ganancia: 520,
            distancia: '3.1 km',
            cliente: 'Ana López',
            direccion_cliente: 'Av. Rivadavia 3456, CABA',
            productos: ['Omeprazol 20mg'],
            total: 300
        }
    ];
    
    // Ordenar por ganancia (mayor a menor)
    pedidosDisponibles.sort((a, b) => b.ganancia - a.ganancia);
    
    renderPedidosDisponibles();
}

function renderPedidosDisponibles() {
    const container = document.getElementById('pedidos-disponibles');
    
    if (pedidosDisponibles.length === 0) {
        container.innerHTML = `
            <div class="text-center py-5">
                <i class="fas fa-inbox fa-3x text-gray-400 mb-3"></i>
                <h3 class="text-gray-600">No hay pedidos disponibles</h3>
                <p class="text-gray-500">Los pedidos aparecerán aquí cuando estén listos para entrega</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = pedidosDisponibles.map(pedido => `
        <div class="pedido-card" onclick="mostrarDetallePedido(${pedido.id})">
            <div class="pedido-card-header">
                <div class="pedido-numero">Pedido #${pedido.numero}</div>
                <div class="pedido-farmacia">
                    <i class="fas fa-store"></i>
                    ${pedido.farmacia}
                </div>
            </div>
            <div class="pedido-card-body">
                <div class="pedido-info">
                    <div class="info-item">
                        <div class="info-label">Ganancia</div>
                        <div class="info-value ganancia">$${pedido.ganancia}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Distancia</div>
                        <div class="info-value distancia">${pedido.distancia}</div>
                    </div>
                </div>
                <div class="pedido-direccion">
                    <div class="direccion-label">
                        <i class="fas fa-map-marker-alt"></i>
                        Dirección de la Farmacia
                    </div>
                    <div class="direccion-text">${pedido.direccion_farmacia}</div>
                </div>
                <div class="pedido-actions">
                    <button class="btn-aceptar" onclick="event.stopPropagation(); aceptarPedido(${pedido.id})">
                        <i class="fas fa-check"></i>
                        Aceptar
                    </button>
                    <button class="btn-rechazar" onclick="event.stopPropagation(); rechazarPedido(${pedido.id})">
                        <i class="fas fa-times"></i>
                        Rechazar
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

/* ===== CARGA DE PEDIDOS ACTIVOS ===== */

function cargarPedidosActivos() {
    console.log('Cargando pedidos activos...');
    
    // Simular datos de pedidos activos
    pedidosActivos = [
        {
            id: 4,
            numero: 'FD20250121004',
            farmacia: 'Farmacia del Centro',
            direccion_farmacia: 'Av. Corrientes 1234, CABA',
            direccion_cliente: 'Av. Santa Fe 5678, CABA',
            cliente: 'Carlos Rodríguez',
            metodo_pago: 'EFECTIVO',
            monto_cobrar: 250,
            productos: ['Amoxicilina 500mg'],
            estado: 'EN_CAMINO'
        }
    ];
    
    renderPedidosActivos();
}

function renderPedidosActivos() {
    const container = document.getElementById('pedidos-activos');
    
    if (pedidosActivos.length === 0) {
        container.innerHTML = `
            <div class="text-center py-5">
                <i class="fas fa-tasks fa-3x text-gray-400 mb-3"></i>
                <h3 class="text-gray-600">No tienes pedidos activos</h3>
                <p class="text-gray-500">Los pedidos que aceptes aparecerán aquí</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = pedidosActivos.map(pedido => `
        <div class="pedido-activo">
            <div class="pedido-activo-header">
                <div class="pedido-activo-info">
                    <div class="pedido-activo-numero">Pedido #${pedido.numero}</div>
                    <div class="pedido-activo-estado">${getEstadoText(pedido.estado)}</div>
                </div>
            </div>
            <div class="pedido-activo-body">
                <div class="direcciones-container">
                    <div class="direccion-section">
                        <div class="direccion-title">
                            <i class="fas fa-store"></i>
                            Recolectar en
                        </div>
                        <div class="direccion-details">
                            <strong>${pedido.farmacia}</strong><br>
                            ${pedido.direccion_farmacia}
                        </div>
                    </div>
                    <div class="direccion-section entrega">
                        <div class="direccion-title entrega">
                            <i class="fas fa-home"></i>
                            Entregar a
                        </div>
                        <div class="direccion-details">
                            <strong>${pedido.cliente}</strong><br>
                            ${pedido.direccion_cliente}
                        </div>
                    </div>
                </div>
                
                <div class="pago-info">
                    <div class="pago-titulo">
                        <i class="fas fa-credit-card"></i>
                        Información de Pago
                    </div>
                    <div class="pago-details">
                        <div class="pago-metodo">${getMetodoPagoText(pedido.metodo_pago)}</div>
                        <div class="pago-monto ${pedido.metodo_pago === 'EFECTIVO' ? 'efectivo' : 'pagado'}">
                            ${pedido.metodo_pago === 'EFECTIVO' ? `$${pedido.monto_cobrar}` : 'Pagado'}
                        </div>
                    </div>
                </div>
                
                <div class="pedido-activo-actions">
                    <button class="btn-entregar" onclick="confirmarEntrega(${pedido.id})">
                        <i class="fas fa-check-circle"></i>
                        Confirmar Entrega Exitosa
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

/* ===== FUNCIONES DE PEDIDOS ===== */

function mostrarDetallePedido(pedidoId) {
    const pedido = pedidosDisponibles.find(p => p.id === pedidoId);
    if (!pedido) return;
    
    const modal = document.getElementById('pedido-modal');
    const modalBody = document.getElementById('modal-body');
    
    modalBody.innerHTML = `
        <div class="pedido-detalle">
            <div class="detalle-header">
                <h4>Pedido #${pedido.numero}</h4>
                <p class="text-muted">${pedido.farmacia}</p>
            </div>
            
            <div class="detalle-info">
                <div class="row mb-3">
                    <div class="col-6">
                        <strong>Ganancia:</strong> $${pedido.ganancia}
                    </div>
                    <div class="col-6">
                        <strong>Distancia:</strong> ${pedido.distancia}
                    </div>
                </div>
                
                <div class="mb-3">
                    <strong>Cliente:</strong> ${pedido.cliente}
                </div>
                
                <div class="mb-3">
                    <strong>Dirección de Entrega:</strong><br>
                    ${pedido.direccion_cliente}
                </div>
                
                <div class="mb-3">
                    <strong>Productos:</strong>
                    <ul class="list-unstyled mt-2">
                        ${pedido.productos.map(producto => `<li><i class="fas fa-pills"></i> ${producto}</li>`).join('')}
                    </ul>
                </div>
                
                <div class="mb-3">
                    <strong>Total del Pedido:</strong> $${pedido.total}
                </div>
            </div>
            
            <div class="detalle-actions">
                <button class="btn btn-success me-2" onclick="aceptarPedido(${pedido.id})">
                    <i class="fas fa-check"></i> Aceptar Pedido
                </button>
                <button class="btn btn-danger" onclick="rechazarPedido(${pedido.id})">
                    <i class="fas fa-times"></i> Rechazar
                </button>
            </div>
        </div>
    `;
    
    modal.classList.add('show');
}

function aceptarPedido(pedidoId) {
    const pedido = pedidosDisponibles.find(p => p.id === pedidoId);
    if (!pedido) return;
    
    // Verificar si ya tiene un pedido activo
    if (pedidosActivos.length > 0) {
        showToast('error', 'Ya tienes un pedido activo', 'Solo puedes tener un pedido activo a la vez');
        return;
    }
    
    // Mover pedido de disponibles a activos
    pedidosActivos.push({
        ...pedido,
        estado: 'EN_CAMINO',
        metodo_pago: 'EFECTIVO',
        monto_cobrar: pedido.total
    });
    
    // Remover de disponibles
    pedidosDisponibles = pedidosDisponibles.filter(p => p.id !== pedidoId);
    
    // Actualizar vistas
    renderPedidosDisponibles();
    renderPedidosActivos();
    
    // Cerrar modal
    document.getElementById('pedido-modal').classList.remove('show');
    
    showToast('success', 'Pedido Aceptado', `Pedido #${pedido.numero} aceptado exitosamente`);
}

function rechazarPedido(pedidoId) {
    const pedido = pedidosDisponibles.find(p => p.id === pedidoId);
    if (!pedido) return;
    
    // Remover de disponibles
    pedidosDisponibles = pedidosDisponibles.filter(p => p.id !== pedidoId);
    
    // Actualizar vista
    renderPedidosDisponibles();
    
    // Cerrar modal
    document.getElementById('pedido-modal').classList.remove('show');
    
    showToast('info', 'Pedido Rechazado', `Pedido #${pedido.numero} rechazado`);
}

function confirmarEntrega(pedidoId) {
    const pedido = pedidosActivos.find(p => p.id === pedidoId);
    if (!pedido) return;
    
    if (confirm(`¿Confirmas que has entregado exitosamente el pedido #${pedido.numero}?`)) {
        // Remover de activos
        pedidosActivos = pedidosActivos.filter(p => p.id !== pedidoId);
        
        // Actualizar vista
        renderPedidosActivos();
        
        showToast('success', 'Entrega Confirmada', `Pedido #${pedido.numero} entregado exitosamente`);
    }
}

/* ===== FUNCIONES AUXILIARES ===== */

function getEstadoText(estado) {
    const estados = {
        'EN_CAMINO': 'En Camino',
        'ENTREGADO': 'Entregado',
        'CANCELADO': 'Cancelado'
    };
    return estados[estado] || estado;
}

function getMetodoPagoText(metodo) {
    const metodos = {
        'EFECTIVO': 'Efectivo',
        'TARJETA_DEBITO': 'Tarjeta de Débito',
        'TARJETA_CREDITO': 'Tarjeta de Crédito',
        'TRANSFERENCIA': 'Transferencia',
        'MERCADO_PAGO': 'Mercado Pago'
    };
    return metodos[metodo] || metodo;
}

/* ===== FUNCIONALIDAD DE MODAL ===== */

function initModal() {
    const modal = document.getElementById('pedido-modal');
    const closeBtn = modal.querySelector('.modal-close');
    
    // Cerrar modal al hacer clic en el botón de cerrar
    closeBtn.addEventListener('click', function() {
        modal.classList.remove('show');
    });
    
    // Cerrar modal al hacer clic fuera del contenido
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            modal.classList.remove('show');
        }
    });
    
    // Cerrar modal con tecla Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && modal.classList.contains('show')) {
            modal.classList.remove('show');
        }
    });
}

/* ===== FUNCIONALIDAD DE TOAST ===== */

function initToast() {
    // Crear contenedor de toasts si no existe
    if (!document.getElementById('toast-container')) {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
}

function showToast(type, title, message) {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const iconClass = {
        'success': 'fas fa-check-circle',
        'error': 'fas fa-exclamation-circle',
        'warning': 'fas fa-exclamation-triangle',
        'info': 'fas fa-info-circle'
    }[type] || 'fas fa-info-circle';
    
    toast.innerHTML = `
        <div class="toast-header">
            <i class="toast-icon ${type} ${iconClass}"></i>
            <span class="toast-title">${title}</span>
        </div>
        <div class="toast-message">${message}</div>
    `;
    
    container.appendChild(toast);
    
    // Auto-remover después de 5 segundos
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 5000);
}

/* ===== FUNCIONALIDAD DE FORMULARIOS ===== */

function initForms() {
    // Formulario de información personal
    const personalForm = document.getElementById('personal-form');
    if (personalForm) {
        personalForm.addEventListener('submit', function(e) {
            e.preventDefault();
            guardarInformacionPersonal();
        });
    }
    
    // Formulario de vehículo
    const vehiculoForm = document.getElementById('vehiculo-form');
    if (vehiculoForm) {
        vehiculoForm.addEventListener('submit', function(e) {
            e.preventDefault();
            guardarInformacionVehiculo();
        });
    }
    
    // Formulario bancario
    const bancarioForm = document.getElementById('bancario-form');
    if (bancarioForm) {
        bancarioForm.addEventListener('submit', function(e) {
            e.preventDefault();
            guardarInformacionBancaria();
        });
    }
}

function guardarInformacionPersonal() {
    const nombre = document.getElementById('nombre').value;
    const email = document.getElementById('email').value;
    const telefono = document.getElementById('telefono').value;
    
    // Simular guardado
    console.log('Guardando información personal:', { nombre, email, telefono });
    
    showToast('success', 'Información Guardada', 'Tu información personal ha sido actualizada');
}

function guardarInformacionVehiculo() {
    const vehiculo = document.getElementById('vehiculo').value;
    const patente = document.getElementById('patente').value;
    const zonaCobertura = document.getElementById('zona_cobertura').value;
    
    // Simular guardado
    console.log('Guardando información del vehículo:', { vehiculo, patente, zonaCobertura });
    
    showToast('success', 'Información Guardada', 'La información de tu vehículo ha sido actualizada');
}

function guardarInformacionBancaria() {
    // Esta función ya no es necesaria ya que eliminamos la sección bancaria
    showToast('info', 'Función no disponible', 'La gestión de información bancaria no está disponible en esta demo');
}

/* ===== FUNCIONES DE UTILIDAD ===== */

function formatCurrency(amount) {
    return new Intl.NumberFormat('es-AR', {
        style: 'currency',
        currency: 'ARS'
    }).format(amount);
}

function formatDistance(distance) {
    return `${distance} km`;
}

// Exportar funciones para uso global
window.mostrarDetallePedido = mostrarDetallePedido;
window.aceptarPedido = aceptarPedido;
window.rechazarPedido = rechazarPedido;
window.confirmarEntrega = confirmarEntrega;
