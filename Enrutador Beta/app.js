document.getElementById('uploadForm').addEventListener('submit', function (e) {
    e.preventDefault();

    const formData = new FormData(this);
    
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.text())
    .then(data => {
        document.getElementById('message').innerText = data;
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('message').innerText = 'Error al cargar el archivo.';
    });
});

// Función para cargar datos en el dashboard
function loadDashboardData() {
    fetch('/api/data') // Endpoint que deberás crear para obtener los datos
        .then(response => response.json())
        .then(data => {
            const tableBody = document.querySelector('#data-table tbody');
            tableBody.innerHTML = ''; // Limpiar la tabla

            data.forEach(row => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${row.id}</td>
                    <td>${row.asesor}</td>
                    <td>${row.numero_nombre_usuario}</td>
                    <td>${row.direccion}</td>
                    <td>${row.barrio_localidad}</td>
                    <td>${row.telefono}</td>
                    <td>${row.fecha_registro}</td>
                    <td>${row.zona_plan_internet}</td>
                    <td>${row.ip}</td>
                    <td>${row.comentarios}</td>
                `;
                tableBody.appendChild(tr);
            });
        })
        .catch(error => console.error('Error al cargar los datos del dashboard:', error));
}

// Cargar datos del dashboard al iniciar la página
document.addEventListener('DOMContentLoaded', loadDashboardData);