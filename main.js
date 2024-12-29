// Exemple : Récupération des capteurs
function loadCapteurs() {
    fetch('/api/capteurs')
        .then(response => response.json())
        .then(data => {
            const table = document.getElementById('capteursTable');
            data.forEach(capteur => {
                const row = table.insertRow();
                row.innerHTML = `<td>${capteur.nom}</td><td>${capteur.etat}</td><td>${capteur.conso}</td>`;
            });
        });
}
