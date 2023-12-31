let currentPage = 1; // Page courante
let totalPages = 1; // Nombre total de pages, initialisé à 1

// Fonction pour tronquer une chaîne de caractères à un certain nombre de mots 
function truncateWords(str, no_words) {
    let mots = str.split(" ");
    let nombre_de_mots = mots.length;
    let chaine = ""
    if (nombre_de_mots > no_words) {
        chaine = str.split(" ").splice(0, no_words).join(" ");
        chaine += "...";
    }
    else {
        chaine = str;
    }

    return chaine;
}

// Fonction pour charger des articles depuis l'API
function loadArticles(category, page = 1) {
    // Faire une requête fetch pour obtenir des articles depuis l'API
    fetch(`/api2/get_articles/?category=${category}&page=${page}`)
        .then(response => response.json())
        .then(data => {
            const articleTableBody = document.getElementById('articleTable');
            articleTableBody.innerHTML = ''; // Effacer le contenu existant du tbody

            totalPages = Math.ceil(data.count / data.resultatPerPage); // Calcule le nombre total de pages
            currentPage = page; // Met à jour la page courante

            // Parcourir chaque article et créer une ligne dans le tableau
            console.log(data)

            data.Articles.forEach(article => {
                const row = document.createElement('tr');
                row.style.height = '100px';
                row.innerHTML = `
                        <td class="align-middle text-center">
                            ${article.image ? `<img src="${article.image}" alt="${article.description}" height='100px'>` : ''}
                        </td>
                    
                        <td class="align-middle" style="font-weight: bold;">
                            ${article.label}
                        </td>

                        <td class="align-middle">
                            
                            ${truncateWords(article.description, 30)}
                        </td>

                        <td class="align-middle">
                            ${article.category_label}
                        </td>
                        
                        <td class="align-middle">
                            ${!article.est_en_promotion ? `${article.price}€TTC` : `<span class="text-decoration-line-through">${article.price}€TTC</span> <span class="text-danger fw-bold">${article.retourner_prix}€TTC</span>`}
                        </td>

                        <td class="align-middle">
                            ${article.est_en_promotion ? `<span class="badge rounded-pill text-bg-danger">${article.valeur_promotion}%</span>` : ''}
                        </td>
                    `;
                articleTableBody.appendChild(row);
            });
            // Mettre à jour l'état des boutons de pagination
            const prevPageButton = document.getElementById('prevPage');
            const nextPageButton = document.getElementById('nextPage');

            if (currentPage <= 1) {
                prevPageButton.setAttribute("disabled", "disabled");
                prevPageButton.classList.add("disabled");
            } else {
                prevPageButton.removeAttribute("disabled");
                prevPageButton.classList.remove("disabled");
            }

            if (currentPage >= totalPages) {
                nextPageButton.setAttribute("disabled", "disabled");
                nextPageButton.classList.add("disabled");
            } else {
                nextPageButton.removeAttribute("disabled");
                nextPageButton.classList.remove("disabled");
            }

        });

}

function prevPage() {
    if (currentPage > 1) {
        loadArticles('', currentPage - 1);
    }
}

function nextPage() {
    if (currentPage < totalPages) {
        loadArticles('', currentPage + 1);
    }
}


// Code qui s'exécute lorsque le DOM est complètement chargé
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