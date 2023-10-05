from django import forms
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import datetime
from django.contrib import admin
from app.models import Article, Category, Promotion


def purger_les_promotions(modeladmin, request, queryset):
    for obj in queryset:
        obj.purger_promotion()


purger_les_promotions.short_description = "Purger les promotions"


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = '__all__'

    def clean_price(self):
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
    # Permet de spécifier le tri d'affichage des catégories sur la vue Admin
    class Meta:
        model = Category
        fields = '__all__'


class CategoryAdmin(admin.ModelAdmin):
    form = CategoryForm
    list_display = ("label",)
    search_fields = ("label",)


class PromotionForm(forms.ModelForm):
    class Meta:
        model = Promotion
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        percent = cleaned_data.get('percent')
        article = cleaned_data.get('article')

        if start_date and end_date:
            if start_date > end_date:
                raise ValidationError(
                    "La date de fin est antérieure à la date de début.")

        if start_date and start_date < datetime.now().date():
            raise ValidationError("La date de début est déjà échue.")

        if percent and not (0 < percent < 50):
            raise ValidationError(
                "La valeur de la promotion ne peut pas dépasser 50%")

        if article is None:
            raise ValidationError(
                "Veuillez sélectionner un article dans la liste")


class PromotionAdmin(admin.ModelAdmin):
    form = PromotionForm
    list_display = ("article", "start_date", "end_date", "percent",)
    actions = [purger_les_promotions]


admin.site.register(Article, ArticleAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Promotion, PromotionAdmin)
