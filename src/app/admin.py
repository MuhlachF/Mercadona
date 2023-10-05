from django import forms
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import datetime
from django.contrib import admin
from app.models import Article, Category, Promotion


def purger_les_promotions(modeladmin, request, queryset):
    """
    Purge les promotions expirées pour les articles sélectionnés dans l'interface d'administration.

    Parameters:
        modeladmin (ModelAdmin): L'instance de ModelAdmin qui gère ce modèle.
        request (HttpRequest): L'objet HttpRequest représentant la requête HTTP en cours.
        queryset (QuerySet): Le QuerySet contenant les objets sélectionnés dans l'interface d'administration.

    Returns:
        None: La méthode ne renvoie rien mais modifie les objets dans la base de données.
    """
    for obj in queryset:
        obj.purger_promotion()


purger_les_promotions.short_description = "Purger les promotions"


class ArticleForm(forms.ModelForm):
    """
    Formulaire pour la gestion des articles dans l'interface d'administration.

    Méthodes:
        clean_price(): Valide et nettoie le champ 'price'.
    """
    class Meta:
        model = Article
        fields = '__all__'

    def clean_price(self):
        """
        Valide et nettoie le champ 'price'.

        Raises:
            ValidationError: Si le prix est invalide.

        Returns:
            Decimal: Le prix validé.
        """
        price = self.cleaned_data.get('price')
        if price is None:
            raise ValidationError("Ce champ est obligatoire !")

        try:
            prix = Decimal(price)
        except:
            raise ValidationError("Veuillez entrer une valeur décimale !")

        if price <= 0:
            raise ValidationError("Le prix ne peut pas être inférieur à 0€")

        return price


class ArticleAdmin(admin.ModelAdmin):
    """
    Configuration de l'interface d'administration pour le modèle Article.

    Attributs:
        form (ModelForm): Le formulaire à utiliser pour la validation.
        list_display (tuple): Les champs à afficher dans la liste des objets.
        list_filter (tuple): Les champs pour lesquels des filtres seront affichés.
        search_fields (tuple): Les champs de recherche.
        readonly_fields (tuple): Les champs en lecture seule.

    Méthodes:
        display_retourner_prix(obj): Affiche le prix après promotion.
        save_model(request, obj, form, change): Sauvegarde le modèle.
    """
    form = ArticleForm
    list_display = ("label", "description", "price",
                    "category", 'image_tag',  "display_retourner_prix", "admin")
    list_filter = ("category", )
    search_fields = ("label", )
    readonly_fields = ('admin',)

    def display_retourner_prix(self, obj):
        return obj.retourner_prix()
    display_retourner_prix.short_description = "Prix après Promotion"

    def save_model(self, request, obj, form, change):
        if not change:  # Si l'objet est en train d'être créé, donc pas modifié
            obj.admin = request.user  # Définir l'administrateur comme l'utilisateur actuel
        obj.save()


class CategoryForm(forms.ModelForm):
    """
    Formulaire pour la gestion des catégories dans l'interface d'administration.
    """

    class Meta:
        model = Category
        fields = '__all__'


class CategoryAdmin(admin.ModelAdmin):
    """
    Configuration de l'interface d'administration pour le modèle Category.

    Attributs:
        form (ModelForm): Le formulaire à utiliser pour la validation.
        list_display (tuple): Les champs à afficher dans la liste des objets.
        search_fields (tuple): Les champs de recherche.
    """
    form = CategoryForm
    list_display = ("label",)
    search_fields = ("label",)


class PromotionForm(forms.ModelForm):
    """
    Formulaire pour la gestion des promotions dans l'interface d'administration.

    Méthodes:
        clean(): Valide et nettoie les champs du formulaire.
    """
    class Meta:
        model = Promotion
        fields = '__all__'

    def clean(self):
        """
        Valide et nettoie les champs du formulaire.
        Cette méthode effectue plusieurs vérifications :
            1. Elle vérifie que la date de début est antérieure à la date de fin.
            2. Elle vérifie que la date de début n'est pas déjà échue.
            3. Elle vérifie que le pourcentage de la promotion est dans une plage acceptable (0 à 50%).
            4. Elle vérifie qu'un article est bien sélectionné dans la liste déroulante.

        Raises:
            ValidationError: Si les données du formulaire sont invalides.

        Returns:
            dict: Les données nettoyées du formulaire.
        """
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        percent = cleaned_data.get('percent')
        article = cleaned_data.get('article')

        # Vérification des dates (1)
        if start_date and end_date:
            if start_date > end_date:
                raise ValidationError(
                    "La date de fin est antérieure à la date de début.")

        # Vérification de la date de début(2)
        if start_date and start_date < datetime.now().date():
            raise ValidationError("La date de début est déjà échue.")

        # Vérification du pourcentage(3)
        if percent and not (0 < percent < 50):
            raise ValidationError(
                "La valeur de la promotion ne peut pas dépasser 50%")

        # Vérification de la sélection d'un article
        if article is None:
            raise ValidationError(
                "Veuillez sélectionner un article dans la liste")


class PromotionAdmin(admin.ModelAdmin):
    """
    Configuration de l'interface d'administration pour le modèle Promotion.

    Attributs:
        form (ModelForm): Le formulaire à utiliser pour la validation.
        list_display (tuple): Les champs à afficher dans la liste des objets.
        actions (list): Les actions à appliquer sur les objets sélectionnés.
    """
    form = PromotionForm
    list_display = ("article", "start_date", "end_date", "percent",)
    actions = [purger_les_promotions]


admin.site.register(Article, ArticleAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Promotion, PromotionAdmin)
