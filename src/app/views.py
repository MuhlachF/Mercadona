from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import ListView

from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import ArticlesSerializer

from .filters import ArticlesFilter

from rest_framework.pagination import PageNumberPagination

from app.models import Article, Category


class AppHome(ListView):

    model = Article
    context_object_name = "Articles"

    # Surcharge de la méthode pour y inclure les catégories
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Ajouter les catégories au contexte
        context['Categories'] = Category.objects.all()

        return context

# Définition de la fonction get_articles qui prend en argument la requête HTTP


def get_articles(request):
    # Récupération de la catégorie depuis les paramètres GET de la requête.
    # Si 'category' n'est pas fournie, None sera utilisé.
    category = request.GET.get('category', None)

    # Filtrage des articles en fonction de la catégorie.
    # Si une catégorie est spécifiée, filtre les articles en conséquence.
    if category:
        articles = Article.objects.filter(category=category)

    # Si aucune catégorie n'est spécifiée, récupère tous les articles.
    else:
        articles = Article.objects.all()

    # Création d'une liste de dictionnaires contenant les informations de chaque article.
    # La liste sera convertie en JSON pour la réponse.
    data = [{"id": article.id,
             "name": article.label,
             "description": article.description,
             "image": article.image.url if article.image else None,
             "category": article.category.label if article.category else None,
             "price": article.price,
             "est_en_promotion": article.est_en_promotion,
             "retourner_prix": article.retour_prix,
             "valeur_promotion": article.valeur_promotion}
            for article in articles]

    # Envoie la réponse en format JSON.
    # L'argument safe=False est nécessaire car nous retournons une liste et non un dictionnaire.
    return JsonResponse(data, safe=False)


@api_view(['GET'])
def get_articles2(request):
    """
    Vue d'API pour récupérer une liste filtrée d'articles.

    Cette fonction utilise django-filters pour appliquer des filtres à la liste d'articles 
    récupérée depuis le modèle `Article`. Elle utilise également la pagination pour limiter 
    le nombre de résultats retournés par requête.

    Parameters:
        request: Objet HttpRequest contenant les métadonnées de la requête HTTP.

    Returns:
        Une réponse HTTP avec la liste paginée et filtrée d'articles sous forme JSON.

    """
    # Applique les filtres sur le queryset en utilisant la classe ArticlesFilter
    filterset = ArticlesFilter(
        request.GET, queryset=Article.objects.all().order_by('label'))

    # Compte le nombre total d'articles après filtrage
    count = filterset.qs.count()

    # Paramètres de la pagination
    resultatPerPage = 5
    paginator = PageNumberPagination()
    paginator.page_size = resultatPerPage

    # Applique la pagination au queryset filtré
    queryset = paginator.paginate_queryset(filterset.qs, request)

    # Sérialisation des objets Article
    serializer = ArticlesSerializer(queryset, many=True)

    # Retourne la réponse

    return Response({"count": count, "resultatPerPage": resultatPerPage, "Articles": serializer.data})
