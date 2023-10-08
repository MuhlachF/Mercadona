from rest_framework import serializers
from .models import Article


class ArticlesSerializer(serializers.ModelSerializer):
    est_en_promotion = serializers.SerializerMethodField()
    category_label = serializers.SerializerMethodField()
    retourner_prix = serializers.SerializerMethodField()
    valeur_promotion = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ('id', 'label', 'description',
                  'image', 'category_label', 'price', 'est_en_promotion', 'retourner_prix', 'valeur_promotion')

    def get_est_en_promotion(self, obj):
        return obj.est_en_promotion

    def get_category_label(self, obj):
        return obj.category.label

    def get_retourner_prix(self, obj):
        return obj.retour_prix

    def valeur_promotion(self, obj):
        return obj.valeur_promotion
