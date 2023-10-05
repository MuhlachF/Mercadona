from django.shortcuts import render

from django.views.generic import ListView

from app.models import Article


class AppHome(ListView):
    paginate_by = 3  # Affiche 10 articles par page
    model = Article
    context_object_name = "Articles"
