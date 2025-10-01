document.addEventListener('DOMContentLoaded', function() {
    console.log("Script control_manual.js cargado.");

    // =========================================================
    // 1. Lógica del Filtro de Rango (Se mantiene igual, solo por completitud)
    // =========================================================
    const rangoSelect = document.getElementById('rango');
    const fechaInicioInput = document.getElementById('fecha_inicio');
    const fechaFinInput = document.getElementById('fecha_fin');

    if (rangoSelect && fechaInicioInput && fechaFinInput) {
        function toggleFechasPersonalizadas() {
            const esPersonalizado = rangoSelect.value === 'personalizado';
            fechaInicioInput.disabled = !esPersonalizado;
            fechaFinInput.disabled = !esPersonalizado;
        }

        toggleFechasPersonalizadas(); 
        rangoSelect.addEventListener('change', toggleFechasPersonalizadas);
    } 

    // =========================================================
    // 2. Inicialización de Gráficos (Chart.js)
    // =========================================================
    
    // **COMPROBACIÓN CRÍTICA DE CARGA**
    if (typeof Chart === 'undefined') {
        console.error("ERROR CRÍTICO: Chart.js no está cargado. Verifique el orden de los scripts en 'extra_js'.");
        return; 
    }
    
    // Función segura para obtener y parsear datos JSON del DOM
    function getParsedData(id, defaultValue = []) {
        const element = document.getElementById(id);
        if (element) {
            try {
                const content = element.textContent.trim();
                // Si el contenido es vacío o Django pasa "None", usamos '[]'
                if (!content || content.toLowerCase() === 'none') {
                     console.warn(`WARN: El elemento #${id} estaba vacío o era "None". Usando array vacío.`);
                    return defaultValue;
                }
                return JSON.parse(content); 
            } catch (error) {
                // **¡SI VES ESTE ERROR EN CONSOLA, EL PROBLEMA ES EN DJANGO VIEW!**
                console.error(`ERROR DE DJANGO: Falló JSON.parse en el elemento #${id}. Esto significa que Django no pasó un JSON válido.`, error);
                console.log(`Contenido que intentó parsear: "${element.textContent}"`);
                return defaultValue; 
            }
        }
        return defaultValue;
    }

    // --- Obtención de Datos Inyectados ---
    const fechasLabels = getParsedData('fechas-labels');
    const totalesData = getParsedData('totales-data');
    const metodosLabels = getParsedData('metodos-labels');
    const metodosData = getParsedData('metodos-data');

    // **DEPURACIÓN CRÍTICA: Muestra los datos que Chart.js va a usar**
    console.log("Datos de Etiquetas (fechasLabels):", fechasLabels);
    console.log("Datos de Valores (totalesData):", totalesData);
    console.log("Etiquetas de Métodos (metodosLabels):", metodosLabels);
    console.log("Datos de Métodos (metodosData):", metodosData);
    
    // 2.1. Gráfico de Evolución de Ventas (Línea)
    const ctxEvolucion = document.getElementById('ventasEvolucionChart');
    if (ctxEvolucion && fechasLabels.length > 0 && totalesData.length > 0) { 
        console.log("Gráfico de Evolución: Inicializando...");
        
        // El resto del código del gráfico de línea se mantiene igual (omito para brevedad)
        new Chart(ctxEvolucion, {
            type: 'line',
            data: {
                labels: fechasLabels,
                datasets: [{
                    label: 'Total Venta en $',
                    data: totalesData,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderWidth: 2,
                    fill: true
                }]
            },
            options: { /* ... options se mantienen ... */ }
        });
    } else if (ctxEvolucion) {
        console.warn("Gráfico de Evolución: No hay suficientes datos para inicializar (fechas o totales vacíos).");
        ctxEvolucion.parentElement.innerHTML = '<p class="text-center text-muted mt-5">No hay suficientes datos de ventas para generar el gráfico en el período seleccionado.</p>';
    }

    // 2.2. Gráfico de Métodos de Pago (Dona/Pie)
    const ctxPagos = document.getElementById('pagosMetodoChart');
    if (ctxPagos && metodosLabels.length > 0 && metodosData.length > 0) {
        console.log("Gráfico de Métodos de Pago: Inicializando...");
        
        const metodosDataTotal = metodosData.reduce((a, b) => a + b, 0); 
        
        // El resto del código del gráfico de Dona se mantiene igual (omito para brevedad)
        new Chart(ctxPagos, {
            type: 'doughnut',
            data: {
                labels: metodosLabels,
                datasets: [{
                    data: metodosData,
                    backgroundColor: [ /* ... colores ... */ ],
                    hoverOffset: 4
                }]
            },
            options: { /* ... options se mantienen ... */ }
        });
    } else if (ctxPagos) {
         console.warn("Gráfico de Métodos de Pago: No hay suficientes datos para inicializar (etiquetas o montos vacíos).");
         ctxPagos.parentElement.innerHTML = '<p class="text-center text-muted mt-5">No hay datos de métodos de pago para generar el gráfico.</p>';
    }
});