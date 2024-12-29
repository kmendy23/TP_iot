document.addEventListener('DOMContentLoaded', () => {
    const meteoButton = document.getElementById('meteoButton');
    const meteoDropdown = document.getElementById('meteo-dropdown');

    // Vérification si les éléments existent pour éviter des erreurs
    if (meteoButton && meteoDropdown) {
        // Ajouter un événement "click" au bouton "Météo"
        meteoButton.addEventListener('click', () => {
            // Basculer l'affichage de la liste déroulante
            if (meteoDropdown.style.display === 'block') {
                meteoDropdown.style.display = 'none';
            } else {
                meteoDropdown.style.display = 'block';
            }
        });
    }
});
