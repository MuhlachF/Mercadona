from django.contrib.auth.models import User
from django.db import models
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from datetime import datetime, date
from decimal import Decimal, ROUND_HALF_UP
from django.utils.html import mark_safe


# Create your models here.


class Category(models.Model):
    """
    Représente une catégorie d'articles dans une boutique en ligne.

    Attributs:
        label (CharField): Le nom unique de la catégorie.

    Méthodes:
        modifier_label_categorie(nouveau_label): Modifie le label de la catégorie.
        lister_categories(): Liste toutes les catégories enregistrées.
        lister_articles_categorie(label_categorie): Liste tous les articles 
            appartenant à une catégorie donnée.
    """
    label = models.CharField(
        max_length=100, unique=True, verbose_name='Catégorie')

    class Meta:
        verbose_name = 'Catégorie'
        ordering = ['label']

    def __str__(self):
        return self.label

    @classmethod
    def lister_categories(cls):
        """
        Liste toutes les catégories enregistrées dans la base de données.

        Returns:
            QuerySet: Un queryset contenant toutes les catégories.
        """
        return Category.objects.all()

    @classmethod
    def lister_articles_categorie(cls, label_categorie):
        """
        Liste tous les articles qui appartiennent à une catégorie donnée.

        Parameters:
            label_categorie (str): Le label de la catégorie dont on souhaite 
            lister les articles.

        Returns:
            QuerySet ou str: Un queryset contenant les articles de la catégorie, 
            ou un message d'erreur si la catégorie n'est pas trouvée.
        """
        try:
            categorie = Category.objects.get(label=label_categorie)
            articles = Article.objects.filter(category=categorie)
            return articles
        except ObjectDoesNotExist:
            return f"Aucune catégorie trouvée avec le label {label_categorie}."


class Article(models.Model):
    """
    Représente un article dans une boutique en ligne.

    Attributs:
        label (CharField): Le nom de l'article, ne peut pas être vide ou null.
        description (TextField): Une description textuelle de l'article, peut être vide.
        price (DecimalField): Le prix de l'article, ne peut pas être vide ou null.
        image (ImageField): Une image représentant l'article, peut être vide ou null.
        admin (ForeignKey): L'administrateur qui a créé ou modifié l'article, peut être null.
        category (ForeignKey): La catégorie à laquelle appartient l'article, peut être null.

    Méthodes:
        promotion_en_cours(): Détermine si l'article est en promotion.
        modifier_article(user, **kwargs): Modifie les attributs de l'article.
        modifier_categorie_article(label_categorie): Modifie la catégorie de l'article.
        promotion_est_valide(strt_date, ed_date): Vérifie la validité d'une période de promotion.
        mettre_article_promotion(valeur_promo, start_date, end_date): Applique une promotion à l'article.
        retourner_prix(): Retourne le prix actuel de l'article, en tenant compte des promotions éventuelles.
    """
    label = models.CharField(max_length=100, blank=False,
                             null=False, verbose_name='Article')
    description = models.TextField(
        blank=True, default="", verbose_name='Description')
    price = models.DecimalField(
        max_digits=6, decimal_places=2, blank=False, null=False, verbose_name='Prix')
    image = models.ImageField(blank=True, null=True,
                              verbose_name='Image', upload_to='app')
    admin = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL, verbose_name='Créateur')
    category = models.ForeignKey(
        "Category", null=True, on_delete=models.SET_NULL, verbose_name='Catégorie')

    class Meta:
        # Nom affiché sur la vue Admin
        verbose_name = 'Article'
        # Permet de spécifier le tri d'affichage des articles sur la vue Admin
        ordering = ['label']

    # Gestion de l'affichage des images des articles sur la vue Admin
    def image_tag(self):
        return mark_safe('<img src="/media/%s" width="100" />' % (self.image))

    image_tag.allow_tags = True

    def promotion_en_cours(self):
        """
        Détermine si l'article est actuellement en promotion.

        Returns:
            Decimal: La valeur en % si en promotion, 0 sinon.
        """

        date_du_jour = date.today()
        articles_promotion = Promotion.objects.filter(article=self)
        for promotion in articles_promotion:
            if promotion.start_date <= date_du_jour <= promotion.end_date:
                return Decimal(promotion.percent)
        return Decimal(0)

    def retourner_prix(self):
        """
        Retourne le prix actuel de l'article, en tenant compte des promotions éventuelles.

        Returns:
        Decimal: Le prix actuel de l'article.
        """
        if self.promotion_en_cours():
            prix = self.price - \
                Decimal(self.price * self.promotion_en_cours() / 100)
            # Permet de gérer les problèmes d'arrondis
            return prix.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)

        else:
            # return self.price.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
            return "Aucune en cours"

    def __str__(self):
        return self.label

    @property
    def est_en_promotion(self):
        if self.promotion_en_cours() == Decimal(0):
            return False
        else:
            return True

    @property
    def valeur_promotion(self):
        return self.promotion_en_cours()


class Promotion(models.Model):
    start_date = models.DateField(verbose_name='Date début de promotion')
    end_date = models.DateField(verbose_name='Date de fin de promotion')
    percent = models.DecimalField(
        max_digits=6, decimal_places=2, verbose_name="Pourcentage de remise")
    article = models.ForeignKey(
        "Article", null=True, on_delete=models.CASCADE, verbose_name='Article')

    def clean(self):
        """
        Vérifie la validité d'une période de promotion pour un article donné.

        Cette méthode effectue plusieurs vérifications :
        1. Elle s'assure qu'aucun chevauchement de dates ne se produit avec les promotions existantes pour l'article en question.
        2. Elle vérifie que la date de début est antérieure à la date de fin.
        3. Elle vérifie que la date de début et la date de fin sont postérieures à la date du jour.
        4. Elle vérifie que le pourcentage de la promotion est bien renseigné et qu'il est dans une plage acceptable (0 à 50%).
        5. Elle vérifie qu'un article est bien sélectionné dans la liste déroulante.

        Raises:
        - ValidationError: Si une des vérifications échoue.

        Returns:
        None: La méthode ne renvoie rien mais lève une exception en cas d'échec de validation.
        """
        articles_promotion = Promotion.objects.filter(article=self.article)
        if articles_promotion.exists():
            for promotion in articles_promotion:
                # Vérifie le chevauchement de dates
                if self.start_date <= promotion.end_date and self.end_date >= promotion.start_date:
                    raise ValidationError(
                        "Une promotion est déjà appliquée sur cette plage")

    def save(self, *args, **kwargs):
        # Appeler la méthode de validation de la promotion avant de sauvegarder
        self.clean()
        # Appeler la méthode 'save' originale
        super(Promotion, self).save(*args, **kwargs)

    @classmethod
    def purger_promotion(cls):
        """
        Supprime toutes les promotions expirées de la base de données.

        Cette méthode parcourt toutes les instances de la classe `Promotion` et supprime celles dont la `end_date` est antérieure à la date du jour.

        Parameters:
        Aucun

        Returns:
        None: La méthode ne renvoie rien, mais supprime les promotions expirées de la base de données.

        Raises:
        ObjectDoesNotExist: Une exception est levée si l'objet promotion n'est pas trouvé, mais est gérée silencieusement dans la méthode.
        """
        date_du_jour = date.today()
        try:
            promotions = cls.objects.all()
            # Recherche des promotions expirées
            for promotion in promotions:
                if date_du_jour > promotion.end_date:
                    promotion.delete()

        except ObjectDoesNotExist:
            raise ObjectDoesNotExist(
                f"Aucune promotion n'a été trouvée pour être purgée.")
