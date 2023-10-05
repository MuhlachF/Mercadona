from django.contrib import admin

from app.models import Article, Category, Promotion


def purger_les_promotions(modeladmin, request, queryset):
    for obj in queryset:
        obj.purger_promotion()


purger_les_promotions.short_description = "Purger les promotions"


class ArticleAdmin(admin.ModelAdmin):
    list_display = ("label", "description", "price",
                    "category", 'image_tag',  "display_retourner_prix", "admin")
    list_filter = ("category", )
    search_fields = ("label", )
    readonly_fields = ('admin',)
    fields = ['image_tag']

    def display_retourner_prix(self, obj):
        return obj.retourner_prix()
    display_retourner_prix.short_description = "Prix après Promotion"

    def save_model(self, request, obj, form, change):
        if not change:  # Si l'objet est en train d'être créé, donc pas modifié
            obj.admin = request.user  # Définir l'administrateur comme l'utilisateur actuel
        obj.save()


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("label",)


class PromotionAdmin(admin.ModelAdmin):
    list_display = ("article", "start_date", "end_date", "percent",)
    actions = [purger_les_promotions]


admin.site.register(Article, ArticleAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Promotion, PromotionAdmin)
