/* ===== JAVASCRIPT PARA PANEL FARMACÉUTICO ===== */

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar funcionalidades
    initTabs();
    initPedidos();
    initInventario();
    initModal();
    initToast();
    
    // Actualizar contadores cada 30 segundos
    setInterval(updateCounters, 30000);
});

/* ===== FUNCIONALIDAD DE PESTAÑAS ===== */

function initTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetTab = this.getAttribute('data-tab');
            
            // Remover clase active de todos los botones y contenidos
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Agregar clase active al botón clickeado y su contenido
            this.classList.add('active');
            document.getElementById(targetTab + '-tab').classList.add('active');
            
            // Cargar contenido específico si es necesario
            if (targetTab === 'inventario') {
                loadInventario();
            } else if (targetTab === 'precios') {
                loadPrecios();
            }
        });
    });
}

/* ===== FUNCIONALIDAD DE PEDIDOS ===== */

function initPedidos() {
    // Event listeners para botones de ver detalle
    document.addEventListener('click', function(e) {
        if (e.target.closest('.ver-detalle')) {
            const pedidoId = e.target.closest('.ver-detalle').getAttribute('data-pedido-id');
            showPedidoModal(pedidoId);
        }
    });
    
    // Event listeners para acciones de pedidos
    document.addEventListener('click', function(e) {
        if (e.target.closest('.confirmar-receta')) {
            const pedidoId = e.target.closest('.confirmar-receta').getAttribute('data-pedido-id');
            confirmarReceta(pedidoId);
        }
        
        if (e.target.closest('.cancelar-receta')) {
            const pedidoId = e.target.closest('.cancelar-receta').getAttribute('data-pedido-id');
            cancelarReceta(pedidoId);
        }
        
        if (e.target.closest('.entregar-repartidor')) {
            const pedidoId = e.target.closest('.entregar-repartidor').getAttribute('data-pedido-id');
            entregarAlRepartidor(pedidoId);
        }
        
        if (e.target.closest('.listo-retiro')) {
            const pedidoId = e.target.closest('.listo-retiro').getAttribute('data-pedido-id');
            listoParaRetiro(pedidoId);
        }
    });
}

function showPedidoModal(pedidoId) {
    const modal = document.getElementById('pedido-modal');
    const modalBody = document.getElementById('modal-body');
    
    // Mostrar loading
    modalBody.innerHTML = '<div class="text-center"><i class="fas fa-spinner fa-spin"></i> Cargando...</div>';
    modal.classList.add('show');
    
    // Cargar contenido del modal
    fetch(`/farmacia/pedido/${pedidoId}/`, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.text())
    .then(html => {
        modalBody.innerHTML = html;
    })
    .catch(error => {
        console.error('Error:', error);
        modalBody.innerHTML = '<div class="text-center text-danger">Error al cargar el pedido</div>';
    });
}

function confirmarReceta(pedidoId) {
    if (!confirm('¿Confirmar que la receta es válida y proceder con la preparación?')) {
        return;
    }
    
    fetch(`/farmacia/pedido/${pedidoId}/confirmar-receta/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('success', 'Éxito', data.mensaje);
            movePedidoToPreparando(pedidoId);
            updateCounters();
        } else {
            showToast('error', 'Error', data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('error', 'Error', 'Error al procesar la solicitud');
    });
}

function cancelarReceta(pedidoId) {
    if (!confirm('¿Está seguro de que la receta es inválida? Esta acción cancelará el pedido.')) {
        return;
    }
    
    fetch(`/farmacia/pedido/${pedidoId}/cancelar-receta/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('success', 'Éxito', data.mensaje);
            removePedidoFromView(pedidoId);
            updateCounters();
        } else {
            showToast('error', 'Error', data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('error', 'Error', 'Error al procesar la solicitud');
    });
}

function entregarAlRepartidor(pedidoId) {
    if (!confirm('¿Confirmar que el pedido fue entregado al repartidor?')) {
        return;
    }
    
    fetch(`/farmacia/pedido/${pedidoId}/entregar-repartidor/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('success', 'Éxito', data.mensaje);
            removePedidoFromView(pedidoId);
            updateCounters();
        } else {
            showToast('error', 'Error', data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('error', 'Error', 'Error al procesar la solicitud');
    });
}

function listoParaRetiro(pedidoId) {
    if (!confirm('¿Marcar el pedido como listo para retiro?')) {
        return;
    }
    
    fetch(`/farmacia/pedido/${pedidoId}/listo-retiro/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('success', 'Éxito', data.mensaje);
            removePedidoFromView(pedidoId);
            updateCounters();
        } else {
            showToast('error', 'Error', data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('error', 'Error', 'Error al procesar la solicitud');
    });
}

function movePedidoToPreparando(pedidoId) {
    const pedidoCard = document.querySelector(`[data-pedido-id="${pedidoId}"]`);
    if (pedidoCard) {
        pedidoCard.classList.add('preparando');
        const preparandoSection = document.getElementById('pedidos-preparando');
        const emptyState = preparandoSection.querySelector('.empty-state');
        
        if (emptyState) {
            emptyState.remove();
        }
        
        preparandoSection.appendChild(pedidoCard);
    }
}

function removePedidoFromView(pedidoId) {
    const pedidoCard = document.querySelector(`[data-pedido-id="${pedidoId}"]`);
    if (pedidoCard) {
        pedidoCard.remove();
        
        // Verificar si quedan pedidos en cada sección
        checkEmptyStates();
    }
    
    // Cerrar modal si está abierto
    const modal = document.getElementById('pedido-modal');
    if (modal.classList.contains('show')) {
        modal.classList.remove('show');
    }
}

function checkEmptyStates() {
    const secciones = ['pedidos-nuevos', 'pedidos-preparando'];
    
    secciones.forEach(seccionId => {
        const seccion = document.getElementById(seccionId);
        const pedidos = seccion.querySelectorAll('.pedido-card');
        
        if (pedidos.length === 0) {
            const emptyState = document.createElement('div');
            emptyState.className = 'empty-state';
            
            if (seccionId === 'pedidos-nuevos') {
                emptyState.innerHTML = '<i class="fas fa-inbox"></i><p>No hay pedidos nuevos</p>';
            } else {
                emptyState.innerHTML = '<i class="fas fa-cog"></i><p>No hay pedidos en preparación</p>';
            }
            
            seccion.appendChild(emptyState);
        }
    });
}

/* ===== FUNCIONALIDAD DE INVENTARIO ===== */

function initInventario() {
    // Event listeners para actualizar stock
    document.addEventListener('click', function(e) {
        if (e.target.closest('.actualizar-stock')) {
            const productoId = e.target.closest('.actualizar-stock').getAttribute('data-producto-id');
            const stockInput = document.querySelector(`input[data-producto-id="${productoId}"]`);
            const nuevoStock = parseInt(stockInput.value);
            
            if (isNaN(nuevoStock) || nuevoStock < 0) {
                showToast('error', 'Error', 'El stock debe ser un número válido mayor o igual a 0');
                return;
            }
            
            actualizarStock(productoId, nuevoStock);
        }
    });
}

function loadInventario() {
    // Esta función se puede usar para cargar datos del inventario dinámicamente
    console.log('Cargando inventario...');
}

function actualizarStock(productoId, nuevoStock) {
    fetch(`/farmacia/inventario/producto/${productoId}/actualizar-stock/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `stock=${nuevoStock}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('success', 'Éxito', data.mensaje);
            updateProductoCard(productoId, nuevoStock);
        } else {
            showToast('error', 'Error', data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('error', 'Error', 'Error al actualizar el stock');
    });
}

function updateProductoCard(productoId, nuevoStock) {
    const productoCard = document.querySelector(`[data-producto-id="${productoId}"]`);
    if (productoCard) {
        // Actualizar clase del card según el stock
        productoCard.classList.remove('sin-stock', 'poco-stock', 'disponible');
        
        if (nuevoStock === 0) {
            productoCard.classList.add('sin-stock');
            moveToSection(productoCard, 'sin-stock');
        } else if (nuevoStock <= 5) {
            productoCard.classList.add('poco-stock');
            moveToSection(productoCard, 'poco-stock');
        } else {
            productoCard.classList.add('disponible');
            moveToSection(productoCard, 'disponible');
        }
    }
}

function moveToSection(productoCard, sectionType) {
    // Encontrar la sección correcta
    const sections = {
        'sin-stock': document.querySelector('.productos-section:nth-child(2) .productos-grid'),
        'poco-stock': document.querySelector('.productos-section:nth-child(3) .productos-grid'),
        'disponible': document.querySelector('.productos-section:nth-child(4) .productos-grid')
    };
    
    const targetSection = sections[sectionType];
    if (targetSection) {
        // Remover de la sección actual
        productoCard.remove();
        
        // Agregar a la nueva sección
        targetSection.appendChild(productoCard);
        
        // Verificar si hay empty states que remover
        checkEmptyStatesInventario();
    }
}

function checkEmptyStatesInventario() {
    const sections = document.querySelectorAll('.productos-grid');
    
    sections.forEach(section => {
        const productos = section.querySelectorAll('.producto-card');
        const emptyState = section.querySelector('.empty-state');
        
        if (productos.length > 0 && emptyState) {
            emptyState.remove();
        } else if (productos.length === 0 && !emptyState) {
            const emptyState = document.createElement('div');
            emptyState.className = 'empty-state';
            emptyState.innerHTML = '<i class="fas fa-boxes"></i><p>No hay productos en esta categoría</p>';
            section.appendChild(emptyState);
        }
    });
}

/* ===== FUNCIONALIDAD DE PRECIOS ===== */

function loadPrecios() {
    // Esta función se puede usar para cargar datos de precios dinámicamente
    console.log('Cargando precios...');
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
    
    // Inicializar modal de receta
    initRecetaModal();
}

function initRecetaModal() {
    const recetaModal = document.getElementById('receta-modal');
    const recetaCloseBtn = recetaModal.querySelector('.modal-receta-close');
    
    // Cerrar modal de receta al hacer clic en el botón de cerrar
    recetaCloseBtn.addEventListener('click', function() {
        recetaModal.classList.remove('show');
    });
    
    // Cerrar modal de receta al hacer clic fuera del contenido
    recetaModal.addEventListener('click', function(e) {
        if (e.target === recetaModal) {
            recetaModal.classList.remove('show');
        }
    });
    
    // Cerrar modal de receta con tecla Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && recetaModal.classList.contains('show')) {
            recetaModal.classList.remove('show');
        }
    });
    
    // Event listener para botones de ver receta
    document.addEventListener('click', function(e) {
        if (e.target.closest('.ver-receta')) {
            const recetaUrl = e.target.closest('.ver-receta').getAttribute('data-receta-url');
            if (recetaUrl) {
                showRecetaModal(recetaUrl);
            }
        }
    });
}

function showRecetaModal(recetaUrl) {
    const recetaModal = document.getElementById('receta-modal');
    const recetaBody = document.getElementById('receta-body');
    
    // Determinar el tipo de archivo
    const extension = recetaUrl.split('.').pop().toLowerCase();
    
    let contenido = '';
    
    if (extension === 'pdf') {
        contenido = `
            <iframe src="${recetaUrl}" class="receta-pdf" frameborder="0">
                <p>Tu navegador no soporta la visualización de PDFs. 
                <a href="${recetaUrl}" target="_blank">Haz clic aquí para descargar el archivo</a></p>
            </iframe>
        `;
    } else if (['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(extension)) {
        contenido = `
            <img src="${recetaUrl}" alt="Receta médica" class="receta-imagen">
        `;
    } else {
        contenido = `
            <div class="text-center p-4">
                <i class="fas fa-file fa-3x text-gray-400 mb-3"></i>
                <p class="text-gray-600">Tipo de archivo no soportado para visualización</p>
                <a href="${recetaUrl}" target="_blank" class="btn btn-primary">
                    <i class="fas fa-download"></i>
                    Descargar Archivo
                </a>
            </div>
        `;
    }
    
    recetaBody.innerHTML = contenido;
    recetaModal.classList.add('show');
}

/* ===== FUNCIONALIDAD DE TOAST ===== */

function initToast() {
    // Crear contenedor de toasts si no existe
    if (!document.getElementById('toast-container')) {
        const toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'toast-container';
        document.body.appendChild(toastContainer);
    }
}

function showToast(type, title, message) {
    const toastContainer = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    toast.innerHTML = `
        <div class="toast-header">
            <div class="toast-title">${title}</div>
            <button class="toast-close" onclick="this.parentElement.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        </div>
        <div class="toast-body">${message}</div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Auto-remover después de 5 segundos
    setTimeout(() => {
        if (toast.parentNode) {
            toast.remove();
        }
    }, 5000);
}

/* ===== FUNCIONES AUXILIARES ===== */

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function updateCounters() {
    // Actualizar contadores de notificaciones
    const pedidosNuevos = document.querySelectorAll('#pedidos-nuevos .pedido-card').length;
    const pedidosPreparando = document.querySelectorAll('#pedidos-preparando .pedido-card').length;
    
    // Actualizar badges
    const badges = document.querySelectorAll('.badge');
    badges.forEach((badge, index) => {
        if (index === 0) { // Badge de pedidos nuevos
            badge.textContent = pedidosNuevos;
        } else if (index === 1) { // Badge de pedidos preparando
            badge.textContent = pedidosPreparando;
        }
    });
    
    // Actualizar contador de notificaciones
    const notificationCount = document.querySelector('.notification-count');
    if (notificationCount) {
        notificationCount.textContent = pedidosNuevos;
    }
}

// Función para formatear fechas
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-AR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Función para formatear moneda
function formatCurrency(amount) {
    return new Intl.NumberFormat('es-AR', {
        style: 'currency',
        currency: 'ARS',
        minimumFractionDigits: 2
    }).format(amount);
}

// Función para validar formularios
function validateForm(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('error');
            isValid = false;
        } else {
            field.classList.remove('error');
        }
    });
    
    return isValid;
}

// Función para mostrar loading en botones
function setButtonLoading(button, loading = true) {
    if (loading) {
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Procesando...';
    } else {
        button.disabled = false;
        button.innerHTML = button.getAttribute('data-original-text') || 'Guardar';
    }
}

// Función para confirmar acciones críticas
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Función para manejar errores de red
function handleNetworkError(error) {
    console.error('Network error:', error);
    showToast('error', 'Error de Conexión', 'No se pudo conectar con el servidor. Verifique su conexión a internet.');
}

// Función para recargar la página después de una acción exitosa
function reloadAfterSuccess(delay = 2000) {
    setTimeout(() => {
        window.location.reload();
    }, delay);
}

// Exportar funciones para uso global
window.FarmaDelivery = {
    showToast,
    confirmAction,
    formatDate,
    formatCurrency,
    validateForm,
    setButtonLoading,
    handleNetworkError,
    reloadAfterSuccess
};
