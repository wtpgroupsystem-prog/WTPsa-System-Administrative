document.addEventListener('DOMContentLoaded', () => {
  const dateInput = document.getElementById('buscarFecha');
  const rows = Array.from(document.querySelectorAll('.tabla-cisternas tbody tr'));

  if (dateInput) {
    dateInput.addEventListener('change', () => {
      const filter = dateInput.value;
      rows.forEach(row => {
        const cell = row.querySelector('td').innerText;
        row.style.display = (filter === "" || cell === filter) ? '' : 'none';
      });
    });
  }
});
