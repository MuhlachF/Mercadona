document.addEventListener('DOMContentLoaded', () => {
    // Charger les articles lors de l'initialisation de la page
    loadArticles('');

    // Mettre à jour les articles lorsque l'utilisateur change de catégorie
    const categorySelector = document.getElementById('categorySelector');
    categorySelector.addEventListener('change', function () {
        console.log(this.value)
        loadArticles(this.value);
    });
});