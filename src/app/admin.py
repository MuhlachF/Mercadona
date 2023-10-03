from django.contrib import admin

from app.models import Article, Category, Promotion


class ArticleAdmin(admin.ModelAdmin):
    list_display = ("label", "description", "price",
                    "image", "admin", "category", "display_retourner_prix")

    def display_retourner_prix(self, obj):
        return obj.retourner_prix()
    display_retourner_prix.short_description = "Prix après Promotion"


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("label",)


class PromotionAdmin(admin.ModelAdmin):
    list_display = ("start_date", "end_date", "percent", "article")


admin.site.register(Article, ArticleAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Promotion, PromotionAdmin)
