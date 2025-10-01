document.addEventListener('DOMContentLoaded', () => {
  // --- Lógica existente para el filtro de búsqueda ---
  const searchInput = document.getElementById('searchDeliveries');
  const rows = Array.from(document.querySelectorAll('.delivery-row'));

  if (searchInput) {
    searchInput.addEventListener('input', () => {
      const q = searchInput.value.trim().toLowerCase();
      rows.forEach(row => {
        row.style.display = row.innerText.toLowerCase().includes(q) ? '' : 'none';
      });
    });
  }

  // --- Nueva lógica para los botones de eliminación ---
  const deleteButtons = document.querySelectorAll('.delete-btn');

  deleteButtons.forEach(button => {
    button.addEventListener('click', (event) => {
      // Previene la acción por defecto del botón (por si está dentro de un formulario)
      event.preventDefault();

      // Obtiene el ID de la entrega del atributo de datos
      const deliveryId = button.dataset.deliveryId;
      console.log(`Intentando eliminar la entrega con ID: ${deliveryId}`);

      // Usar un fetch para enviar una solicitud POST al servidor para eliminar la entrega.
      // Es necesario incluir el token CSRF de Django en la cabecera.
      const csrfToken = getCookie('csrftoken');

      // Se usa un `fetch` con el método POST para coincidir con la función `delete_delivery` en Django.
      fetch(`/delete-delivery/${deliveryId}/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrfToken,
          'Content-Type': 'application/json'
        }
      })
      .then(response => {
        if (response.ok) {
          // Si la solicitud fue exitosa, recarga la página para mostrar la lista actualizada.
          // El servidor de Django ya redirige a la página 'deliveries' después de la eliminación.
          window.location.reload();
        } else {
          // Si hubo un error, muestra un mensaje en la consola.
          console.error('Error al eliminar la entrega.');
        }
      })
      .catch(error => {
        console.error('Error en la solicitud:', error);
      });
    });
  });

  // Función auxiliar para obtener el token CSRF del navegador
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        // ¿Empieza este string de cookie con el nombre que queremos?
        if (cookie.startsWith(name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
});
