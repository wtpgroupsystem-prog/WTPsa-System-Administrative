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

const csrftoken = getCookie('csrftoken');

function restarBotella(promoId) {
    fetch(`/promos/restar/${promoId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json'
        }
    }).then(response => response.json())
      .then(data => {
          if (data.success) {
              const row = document.getElementById(`promo-${promoId}`);
              // Actualizamos el número de botellas pendientes
              row.querySelector('.botellas-pendientes').textContent = data.botellas_restantes;
              // Si no quedan botellas, eliminamos la fila
              if (data.botellas_restantes === 0) {
                  row.remove();
              }
          } else {
              alert(data.error || "Error al restar botella");
          }
      }).catch(error => {
          console.error('Error:', error);
          alert('Hubo un problema al conectar con el servidor.');
      });
}