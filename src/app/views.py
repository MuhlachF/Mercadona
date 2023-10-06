from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import ListView

from app.models import Article, Category


class AppHome(ListView):
    paginate_by = 10  # Affiche 10 articles par page

    model = Article
    context_object_name = "Articles"

    # Surcharge de la méthode pour y inclure les catégories
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Ajouter les catégories au contexte
        context['Categories'] = Category.objects.all()

        return context


def get_articles(request):
    category = request.GET.get('category', None)
    if category:
        articles = Article.objects.filter(category=category)
    else:
        articles = Article.objects.all()
    data = [{"id": article.id, "name": article.label} for article in articles]
    return JsonResponse(data, safe=False)
