document.addEventListener('DOMContentLoaded', function() {
  // ——— Gráfico de Agua Disponible ———
  const canvasAgua = document.getElementById('aguaChart');
  const litros = parseFloat(canvasAgua.dataset.litros) || 0;
  const ctx1 = canvasAgua.getContext('2d');
  new Chart(ctx1, {
    type: 'bar',
    data: {
      labels: ['Agua Restante'],
      datasets: [{
        label: 'Litros Disponibles',
        data: [litros],
        backgroundColor: ['rgba(59, 130, 246, 0.7)'],
        borderColor: ['rgba(59, 130, 246, 1)'],
        borderWidth: 1
      }]
    },
    options: {
      scales: {
        y: {
          beginAtZero: true,
          max: 10000
        }
      },
      plugins: {
        legend: { position: 'bottom' },
        title: {
          display: true,
          text: 'Agua Disponible en Litros'
        }
      }
    }
  });

  // ——— Gráfico de Ventas Diarias ———
  const canvasVentas = document.getElementById('ventasChart');
  // obtenemos los arrays desde data-attributes
  const labels = JSON.parse(document.getElementById('labels').textContent);
  const values = JSON.parse(document.getElementById('values').textContent);
  const ctx2 = canvasVentas.getContext('2d');
  new Chart(ctx2, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'Ventas Diarias (L)',
        data: values,
        borderColor: 'rgba(34, 197, 94, 1)',
        backgroundColor: 'rgba(34, 197, 94, 0.2)',
        fill: true,
        tension: 0.4
      }]
    },
    options: {
      scales: {
        y: { beginAtZero: true }
      },
      plugins: {
        title: {
          display: true,
          text: 'Ventas Diarias'
        }
      }
    }
  });
});
