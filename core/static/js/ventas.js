document.addEventListener('DOMContentLoaded', function() {
    // Referencias a los elementos del DOM
    const ventaForm = document.getElementById('venta-form');
    const codigoInput = document.getElementById('producto-codigo');
    const addItemBtn = document.getElementById('add-item-btn');
    const listaItems = document.getElementById('lista-items');
    const pagosContainer = document.getElementById('pagos-container');
    const addPagoBtn = document.getElementById('add-pago-btn');
    
    // IDs para los totales
    const totalPagarDivisaSpan = document.getElementById('total-a-pagar-divisa'); 
    const totalPagarBsdSpan = document.getElementById('total-a-pagar-bsd');       
    const saldoPendienteSpan = document.getElementById('saldo-pendiente');
    const finalizarBtn = document.getElementById('finalizar-btn');
    
    const pagosDataInput = document.getElementById('pagos-data');
    const itemsDataInput = document.getElementById('items-data');
    const messageContainer = document.getElementById('message-container');
    
    // --- Carga y mapeo de datos del backend ---
    const productosDataElement = document.getElementById('productos-data');
    const metodosPagoDataElement = document.getElementById('metodos-pago-data');
    const tasaActualElement = document.getElementById('tasa-actual-data');

    // Deserialización de los datos (Asegurando la robustez)
    let productosData = [];
    let metodosPagoData = [];
    let tasaActual = 0;

    try {
        if (productosDataElement && productosDataElement.textContent) {
            productosData = JSON.parse(productosDataElement.textContent.trim() || '[]');
        }
        if (metodosPagoDataElement && metodosPagoDataElement.textContent) {
            metodosPagoData = JSON.parse(metodosPagoDataElement.textContent.trim() || '[]');
        }
        if (tasaActualElement && tasaActualElement.textContent) {
            const tasaStr = JSON.parse(tasaActualElement.textContent.trim()); 
            tasaActual = parseFloat(tasaStr) || 0;
        }
    } catch (e) { 
        console.error('Error al parsear datos de Django:', e);
        showMessage('Error crítico al cargar datos del sistema (precios, tasa). Recargue la página.', 'danger');
    }

    const productosMap = new Map();
    if (Array.isArray(productosData)) {
        productosData.forEach(p => productosMap.set(String(p.codigo), p));
    }
    
    const metodosPagoMap = new Map();
    if (Array.isArray(metodosPagoData)) {
        metodosPagoData.forEach(m => metodosPagoMap.set(m.nombre, m));
    }

    // Almacén de ítems y pagos en el cliente
    let currentItems = [];
    let currentPagos = [];

    // Función auxiliar para redondear a 2 decimales
    const roundToTwoDecimals = (num) => Math.round(num * 100) / 100;
    
    // --- Funciones de Lógica de Negocio ---
    
    function showMessage(message, type = 'info') {
        if (messageContainer) {
            messageContainer.innerHTML = '';
            const alertHtml = `<div class="alert alert-${type} alert-dismissible fade show" role="alert">${message}<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>`;
            messageContainer.innerHTML = alertHtml;
        } else {
            console.error('messageContainer not found');
        }
    }

    function actualizarTotales() {
        let totalVentaDivisa = 0;
        let totalPagadoDivisa = 0;

        // 1. Calcular el total de la venta en USD
        currentItems.forEach(item => {
            const producto = productosMap.get(item.codigo);
            if (producto) {
                // ✅ CORRECCIÓN CLAVE: Convertir el precio a float y validar
                const precio = parseFloat(producto.precio_divisa); 
                
                if (!isNaN(precio) && precio > 0) {
                    totalVentaDivisa += precio * item.cantidad;
                }
            }
        });
        
        // Redondear totalVentaDivisa 
        totalVentaDivisa = roundToTwoDecimals(totalVentaDivisa);

        // 2. Calcular el total de pagos en USD
        currentPagos.forEach(pago => {
            const monto = roundToTwoDecimals(pago.monto);
            const metodo = metodosPagoMap.get(pago.metodo_pago);
            
            if (metodo && !isNaN(monto) && monto > 0) {
                if (metodo.es_bolivares && tasaActual > 0) {
                    // Conversión de BsD a $
                    totalPagadoDivisa += monto / tasaActual;
                } else {
                    // Pago ya en $
                    totalPagadoDivisa += monto;
                }
            }
        });
        
        // Redondear totalPagadoDivisa
        totalPagadoDivisa = roundToTwoDecimals(totalPagadoDivisa);

        // 3. Cálculos finales
        const totalVentaBsd = totalVentaDivisa * tasaActual;
        
        // Saldo pendiente: Positivo=falta, Negativo=cambio
        let saldoPendiente = totalVentaDivisa - totalPagadoDivisa;
        saldoPendiente = roundToTwoDecimals(saldoPendiente);
        
        // Usamos una tolerancia de 0.01 para verificar si está 'pagado'
        const isPaid = Math.abs(saldoPendiente) < 0.01;
        
        // 4. Actualizar la interfaz
        
        // Total a Pagar
        if (totalPagarDivisaSpan) {
            totalPagarDivisaSpan.textContent = `$${totalVentaDivisa.toFixed(2)}`;
        }
        if (totalPagarBsdSpan) {
            totalPagarBsdSpan.textContent = `BsD ${totalVentaBsd.toFixed(2)}`;
        }
        
        // Saldo Pendiente
        if (saldoPendienteSpan) {
            saldoPendienteSpan.classList.remove('text-success', 'text-danger');
            
            if (isPaid) {
                 // Pagado o cambio insignificante
                 saldoPendienteSpan.textContent = `$0.00`;
                 saldoPendienteSpan.classList.add('text-success');
            } else if (saldoPendiente > 0) {
                 // Falta dinero
                 saldoPendienteSpan.textContent = `$${saldoPendiente.toFixed(2)}`;
                 saldoPendienteSpan.classList.add('text-danger');
            } else {
                 // Cambio (es negativo)
                 saldoPendienteSpan.textContent = `$${Math.abs(saldoPendiente).toFixed(2)}`;
                 saldoPendienteSpan.classList.add('text-success');
            }
        }

        // 5. Habilitar/deshabilitar el botón de finalizar
        if (finalizarBtn) {
            const hayItems = currentItems.length > 0;
            
            finalizarBtn.disabled = !(isPaid && hayItems);
            
            if (!hayItems) {
                 finalizarBtn.textContent = 'Añada Productos';
            } else if (saldoPendiente > 0) {
                finalizarBtn.textContent = `Faltan $${saldoPendiente.toFixed(2)}`;
            } else if (saldoPendiente < -0.01) {
                finalizarBtn.textContent = `Cambio: $${Math.abs(saldoPendiente).toFixed(2)}`;
            } else {
                finalizarBtn.textContent = 'Finalizar Venta';
            }
        }
    }
    
    // --- Funciones de UI ---

    function renderItems() {
        if (!listaItems) return;
        listaItems.innerHTML = '';
        currentItems.forEach((item, index) => {
            const producto = productosMap.get(item.codigo);
            if (!producto) return;

            const cantidadDisplay = producto.tipo === 'agua_litros' ? item.cantidad : Math.round(item.cantidad);
            const precio = parseFloat(producto.precio_divisa);
            const subtotalDivisa = roundToTwoDecimals(precio * item.cantidad);

            const li = document.createElement('li');
            li.classList.add('list-group-item', 'd-flex', 'justify-content-between', 'align-items-center');
            
            li.innerHTML = `
                ${producto.nombre} x ${cantidadDisplay} - <strong>$${subtotalDivisa.toFixed(2)}</strong>
                <button type="button" class="btn btn-danger btn-sm remove-item-btn">
                    <i class="fas fa-trash"></i>
                </button>
            `;
            listaItems.appendChild(li);

            li.querySelector('.remove-item-btn').addEventListener('click', function() {
                // Eliminar por índice para simplificar
                currentItems.splice(index, 1); 
                renderItems();
                actualizarTotales();
            });
        });
    }

    function crearCampoPago() {
        if (!pagosContainer) return;
        
        if (!Array.isArray(metodosPagoData) || metodosPagoData.length === 0) {
            showMessage("Error al cargar métodos de pago. Verifique los datos del backend.", 'danger');
            return;
        }

        const row = document.createElement('div');
        row.classList.add('pago-row', 'input-group', 'mb-2');
        
        const metodosNombres = metodosPagoData.map(m => m.nombre);

        row.innerHTML = `
            <input type="number" step="0.01" class="form-control monto-pago-input" placeholder="Monto" required>
            <select class="form-select metodo-pago-select">
                ${metodosNombres.map(nombre => `<option value="${nombre}">${nombre}</option>`).join('')}
            </select>
            <button type="button" class="btn btn-danger remove-pago-btn">
                <i class="fas fa-trash"></i>
            </button>
        `;
        pagosContainer.appendChild(row);

        // Ejecutar funciones de recolección y actualización
        const updateFunctions = () => {
            recolectarPagos();
            actualizarTotales();
        };

        row.querySelector('.remove-pago-btn').addEventListener('click', function() {
            row.remove();
            updateFunctions();
        });

        row.querySelector('.monto-pago-input').addEventListener('input', updateFunctions);
        row.querySelector('.metodo-pago-select').addEventListener('change', updateFunctions);
        
        // Si es el primer pago, enfocarse y actualizar totales
        if (currentPagos.length === 0) {
            row.querySelector('.monto-pago-input').focus();
        }
        
        updateFunctions();
    }

    function recolectarPagos() {
        currentPagos = [];
        document.querySelectorAll('.pago-row').forEach(row => {
            const monto = parseFloat(row.querySelector('.monto-pago-input').value);
            const metodo = row.querySelector('.metodo-pago-select').value;
            // Solo añadir si el monto es un número válido y positivo
            if (!isNaN(monto) && monto > 0) {
                currentPagos.push({
                    monto: monto,
                    metodo_pago: metodo
                });
            }
        });
    }

    // --- Eventos ---
    if (addItemBtn) {
        addItemBtn.addEventListener('click', function() {
            const codigo = codigoInput.value.trim();
            if (!codigo) { 
                showMessage('Ingrese un código de producto.', 'warning');
                return; 
            }
    
            const producto = productosMap.get(String(codigo));
            if (!producto) {
                showMessage('Producto no encontrado.', 'danger');
                return;
            }
    
            let cantidad = 1;
            // Manejo especial para productos de tipo 'agua_litros'
            if (producto.tipo === 'agua_litros') {
                const cantidadPrompt = prompt("Ingrese la cantidad de litros:");
                if (cantidadPrompt === null || isNaN(parseFloat(cantidadPrompt)) || parseFloat(cantidadPrompt) <= 0) {
                    showMessage('Cantidad de litros inválida.', 'warning');
                    return;
                }
                cantidad = parseFloat(cantidadPrompt);
            }
    
            // Añadir o actualizar el ítem
            const itemExistente = currentItems.find(item => String(item.codigo) === String(codigo));
            if (itemExistente) {
                itemExistente.cantidad += cantidad;
            } else {
                currentItems.push({
                    codigo: String(producto.codigo),
                    cantidad: cantidad,
                });
            }
            
            codigoInput.value = '';
            renderItems();
            actualizarTotales();
        });
    }

    if (ventaForm) {
        ventaForm.addEventListener('submit', function(e) {
            // Re-validar antes de enviar
            recolectarPagos();
            actualizarTotales(); 
            
            if (finalizarBtn.disabled) {
                e.preventDefault();
                return;
            }
    
            // Empaquetar los datos JSON para Django
            if (itemsDataInput) {
                itemsDataInput.value = JSON.stringify(currentItems);
            }
            if (pagosDataInput) {
                pagosDataInput.value = JSON.stringify(currentPagos);
            }
            // La validación CSRF se maneja por Django con la etiqueta {% csrf_token %} en el HTML
        });
    }

    if (addPagoBtn) {
        addPagoBtn.addEventListener('click', crearCampoPago);
    }

    // Inicialización: Crear un campo de pago si no existe
    if (pagosContainer && pagosContainer.children.length === 0) {
        crearCampoPago();
    } else {
        actualizarTotales();
    }
});