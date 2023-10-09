from django_filters import rest_framework as filters
from .models import Article


class ArticlesFilter(filters.FilterSet):
    """
    Cette classe hérite de `filters.FilterSet` et sert à définir des filtres 
    personnalisés pour le modèle `Article`.

    Attributes:
        Meta: Une classe imbriquée qui contient des métadonnées pour le modèle 
              `Article`, comme les champs sur lesquels filtrer.
    """

    class Meta:
        """
        Une classe imbriquée pour définir les métadonnées du modèle `Article` 
        à utiliser pour le filtrage.

        Attributes:
            model: Le modèle de données sur lequel appliquer les filtres, ici `Article`.
            fields: le seul tuple sur lesquel appliquer le filtre, ici la catégory (id).
        """
        model = Article
        fields = ('category',)
