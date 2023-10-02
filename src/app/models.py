from django.contrib.auth import get_user_model
from django.db import models
from django.core.exceptions import ObjectDoesNotExist, FieldError
from datetime import datetime, date
from django.contrib.auth.decorators import login_required

User = get_user_model()

# Create your models here.


class Category(models.Model):
    """
    Représente une catégorie d'articles dans une boutique en ligne.

    Attributs:
        label (CharField): Le nom unique de la catégorie.
        admin (ForeignKey): L'administrateur qui a créé la catégorie.

    Méthodes:
        lister_categories(): Liste toutes les catégories.
        lister_articles_categorie(label_categorie): Liste tous les articles 
        appartenant à une catégorie donnée.
    """
    label = models.CharField(max_length=100, unique=True)

    def modifier_label_categorie(self, nouveau_label):
        """
        Modifie le label d'une catégorie existante.

        Cette méthode prend en paramètre un objet `categorie` et un `nouveau_label`. 
        Elle vérifie d'abord que l'objet fourni est bien une instance de la classe `Categorie`, 
        puis elle met à jour le label de la catégorie.

        Parameters:
        - categorie (Categorie): L'objet catégorie dont le label doit être modifié.
        - nouveau_label (str): Le nouveau label pour la catégorie.

        Returns:
        str: un message indiquant la réussite de l'opération de modification

        Raises:
        TypeError: Si l'objet fourni n'est pas une instance de la classe `Categorie`.
        """

        try:
            existing_category = Category.objects.get(label=nouveau_label)
            if existing_category:
                return f"La catégorie {nouveau_label} existe déjà"
        except Category.DoesNotExist:
            pass

        self.label = nouveau_label
        self.save()

        return f"Le nouveau label {nouveau_label} a été appliqué à la catégorie"

    @staticmethod
    def lister_categories():
        """
        Liste toutes les catégories enregistrées dans la base de données.

        Returns:
            QuerySet: Un queryset contenant toutes les catégories.
        """
        return Category.objects.all()

    def lister_articles_categorie(label_categorie):
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
            articles = Article.objects.filter(cat=categorie)
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
        cat (ForeignKey): La catégorie à laquelle appartient l'article, peut être null.

    Notes:
        Les attributs 'admin' et 'cat' sont des clés étrangères. 
        Ils sont définis comme pouvant être null, ce qui signifie que l'article peut exister 
        sans administrateur ou catégorie associée.
    """
    label = models.CharField(max_length=100, blank=False, null=False)
    description = models.TextField(blank=True, default="")
    price = models.DecimalField(
        max_digits=6, decimal_places=2, blank=False, null=False)
    image = models.ImageField(blank=True, null=True)
    admin = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL)
    category = models.ForeignKey(
        "Category", null=True, on_delete=models.SET_NULL)

    def promotion_en_cours(self):
        """
        Détermine si l'article est actuellement en promotion.

        Cette méthode vérifie si l'article est lié à une promotion active. 
        Pour cet exemple, nous supposons qu'une promotion est "active" si elle 
        est présente dans la base de données.

        Returns:
            bool: True si en promotion, False sinon.
        """
        date_du_jour = date.today()
        articles_promotion = Promotion.objects.filter(article=self)
        for promotion in articles_promotion:
            if promotion.start_date <= date_du_jour <= promotion.end_date:
                return promotion.percent
        return False

    def retourner_prix(self):
        pass

    def modifier_article(self, **kwargs):
        """
        Modifie les attributs d'une instance d'Article.

        Cette méthode prend une instance d'Article et un ensemble indéfini 
        d'arguments mot-clé,puis modifie les attributs de l'article en fonction 
        des arguments fournis.
        Si des modifications sont effectuées, l'attribut 'admin' de l'article 
        est également mis à jour pour référencer l'administrateur actuel.

        Parameters:
        - article (Article): L'instance de l'Article à modifier
        - **kwargs: Dictionnaire contenant les champs à modifier et les nouvelles valeurs

        Returns:
        str: un message indiquant la réussite de l'opération de modification

        Raises:
        - TypeError: Si l'objet passé n'est pas une instance de la classe Article
        - FieldError: Si un des champs spécifiés n'existe pas dans la classe Article
        """

        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
                modificiations_effectuees = True

            else:
                raise FieldError(f"Le champ {key} n'a pas été trouvé")

            if modificiations_effectuees:
                setattr(self, "admin", User)
                self.save()
                modificiations_effectuees = False
        return f"La modificiation de l'article {self} a été effectuée avec succès"

    def modifier_categorie_article(self, label_categorie):
        """
        Modifie la catégorie d'un article existant.

        Cette méthode prend en paramètres un objet `article` de type Article et un label 
        de catégorie en texte simple.
        Elle recherche une catégorie avec le label correspondant dans la base de données. 
        Si une telle catégorie existe, l'objet `article` est mis à jour avec cette nouvelle catégorie.

        Parameters:
        - article (Article): L'objet Article dont la catégorie doit être modifiée.
        - label_categorie (str): Le label de la nouvelle catégorie que l'article doit avoir.

        Returns:
        str: Un message d'erreur si la catégorie n'est pas trouvée et un message de modification si l'opération a réussi

        Raises:
        - TypeError: Si l'objet `article` passé n'est pas une instance de la classe Article.
        - ObjectDoesNotExist: Si la catégorie avec le label spécifié n'existe pas.
        """

        try:
            label_cat = Category.objects.get(label=label_categorie)
            self.category = label_cat
            self.save()
            return f"{self.label} est à présent intégré dans la catégorie {label_categorie}"
        except ObjectDoesNotExist:
            return f"La catégorie {label_categorie} n'existe pas."

    def mettre_article_promotion(self, valeur_promo, start_date, end_date):
        """
        Applique une promotion à un article donné pour une période de temps spécifiée.

        Cette méthode crée une nouvelle instance de la classe `Promotion` associée à un article donné,
        et enregistre cette instance dans la base de données.

        Parameters:
        - article (Article): L'instance de l'Article sur lequel appliquer la promotion.
        - valeur_promo (int): La valeur de la réduction en pourcentage (doit être entre 0 et 80).
        - start_date (datetime.date): La date de début de la promotion.
        - end_date (datetime.date): La date de fin de la promotion.

        Returns:
        None: Si la promotion est créée avec succès, aucune valeur n'est retournée.

        Raises:
        - TypeError: Si l'objet `article` passé n'est pas une instance de la classe Article.
        - ValueError: Si la valeur de la promotion n'est pas entre 0 et 80.
        - ObjectDoesNotExist: Si la création de la promotion échoue pour une raison quelconque (gérée silencieusement).
        """
        # Vérification de la validité des dates
        if start_date < datetime.now().date() or end_date < datetime.now().date():
            raise ObjectDoesNotExist(
                "La date de début ou de fin est dans le passé.")
        # Vérification de la plage
        if not (0 < valeur_promo < 80):
            raise ValueError(
                "La valeur de la promotion doit être comprise entre 0 et 80%")
        try:
            if self.promotion_est_valide(start_date, end_date):

                # Création de l'objet Article
                new_promotion = Promotion(
                    article=self,
                    percent=valeur_promo,
                    start_date=start_date,
                    end_date=end_date,
                    admin=self,  # L'administrateur qui crée l'article
                )
                new_promotion.save()
                return f"La promotion a été créée sur l'article {self.label} et débutera le {start_date} et prendra fin le {end_date}"
        except ObjectDoesNotExist:
            raise ObjectDoesNotExist(f"L'objet n'existe pas.")

    def promotion_est_valide(self, strt_date, ed_date):
        """
        Vérifie la validité d'une période de promotion pour un article donné.

        Cette méthode vérifie si une nouvelle promotion peut être ajoutée en s'assurant 
        qu'aucun chevauchement de dates ne se produit avec les promotions existantes pour cet article.
        Elle vérifie également que la date de début est antérieure à la date de fin et que la date de fin
        est postérieure à la date du jour.

        Parameters:
        - strt_date (date): La date de début de la nouvelle promotion
        - ed_date (date): La date de fin de la nouvelle promotion

        Returns:
        bool: True si la période de la promotion est valide, sinon False.
        """
        date_du_jour = date.today()
        # Vérifie que la date de début est antérieure à la date de fin
        if strt_date > ed_date:
            return False

        # Vérifie si la date de fin est valide
        if date_du_jour > ed_date:
            return False

        # Recherche toutes les promotions associées à cet article
        articles_promotion = Promotion.objects.filter(article=self)
        if articles_promotion.exists():
            for promotion in articles_promotion:
                # Vérifie le chevauchement de dates
                if strt_date <= promotion.end_date and ed_date >= promotion.start_date:
                    return False
        return True


class Promotion(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()
    percent = models.DecimalField(max_digits=6, decimal_places=2)
    article = models.ForeignKey("Article", on_delete=models.CASCADE)
    admin = models.ForeignKey(User, on_delete=models.CASCADE)

    def purger_promotion(self):
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
            promotions = self.objects.all()
            # Recherche des promotions expirées
            for promotion in promotions:
                if date_du_jour > promotion.end_date:
                    promotion.delete()

        except ObjectDoesNotExist:
            raise ObjectDoesNotExist(
                f"Aucune promotion n'a été trouvée pour être purgée.")
