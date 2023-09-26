from django.db import models
from django.core.exceptions import ObjectDoesNotExist, FieldError
from datetime import datetime, date

# Create your models here.


class Administrator(models.Model):
    """
    La classe Administrator est responsable de la gestion des articles,
    des promotions et des catégories. Elle offre des méthodes CRUD pour 
    accomplir ces tâches.
    """

    name = models.CharField(max_length=255, blank=False, null=False)
    last_name = models.CharField(max_length=255, blank=False, null=False)
    pseudo = models.CharField(max_length=100, blank=False, null=False)
    email = models.EmailField(unique=True, blank=False, null=False)
    password = models.CharField(max_length=255, blank=False, null=False)

    def creer_article(self, label, price, description=None, image=None, category=None):
        """
        Crée un nouvel article et le sauvegarde dans la base de données.

        Parameters:
        - label (str): Le libellé de l'article
        - description (str): La description de l'article
        - price (float): Le prix de l'article

        Returns:
        str: Un message indiquant le succès ou l'échec de l'opération de création.
        """

        # Valider les données en entrée
        if not label or not price:
            return f"Le prix ou l'étiquette n'est pas renseigné"

        # Création de l'objet Article
        new_article = Article(
            label=label,
            description=description or "",
            price=price,
            image=image,
            admin=self,  # L'administrateur qui crée l'article
            cat=category,  # La catégorie à laquelle l'article appartient
        )
        new_article.save()

        return f"L'article {label} au prix de {price} €TTC appartenant à la categorie {category.label} a été créé"

    def supprimer_article(self, article_id):
        """
        Supprime un article de la base de données en utilisant son ID.

        Parameters:
        - article_id (int): L'ID de l'article à supprimer

        Returns:
        str: Un message indiquant le succès ou l'échec de l'opération de suppression.

        Raises:
        - ObjectDoesNotExist: Si aucun article avec l'ID spécifié n'est trouvé
        """

        try:
            article = Article.objects.get(id=article_id)
            article.delete()
            return f"Article avec l'ID {article_id} a été supprimé."
        except ObjectDoesNotExist:
            return f"Aucun article trouvé avec l'ID {article_id}."

    def modifier_article(self, article, **kwargs):
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
        if not isinstance(article, Article):
            raise TypeError(
                "L'objet fourni n'est pas une instance de la classe Article.")
        modificiations_effectuees = False
        for key, value in kwargs.items():
            if hasattr(article, key):
                setattr(article, key, value)
                modificiations_effectuees = True

            else:
                raise FieldError(f"Le champ {key} n'a pas été trouvé")

            if modificiations_effectuees:
                setattr(article, "admin", self)
                article.save()
                modificiations_effectuees = False
        return f"La modificiation de l'article {article} a été effectuée avec succès"

    def creer_categorie(self, label):
        """
        Crée une nouvelle catégorie dans la base de données.

        Cette méthode prend une chaîne de caractères pour le libellé de la catégorie, 
        crée une nouvelle instance de la classe Category avec ce libellé, et l'enregistre dans la base de données. 
        L'attribut 'admin' de la catégorie est également mis à jour pour référencer l'administrateur actuel.

        Parameters:
        - label (str): Le libellé de la nouvelle catégorie

        Returns:
        str: Un message indiquant le succès ou l'échec de l'opération de création.

        """
        # Valider les données en entrée
        # print(Category.objects.get(label))
        if not label:
            return f"Le label n'est pas renseigné"

        try:
            existing_category = Category.objects.get(label=label)
            return f"La catégorie {existing_category.label} est déjà présente dans la base de données"
        except ObjectDoesNotExist:
            pass  # continuez le code si la catégorie n'existe pas

        # Création de l'objet catégorie
        new_category = Category(
            label=label,
            admin=self,  # L'administrateur qui crée la catégorie
        )
        new_category.save()

        return f"La catégorie {label} a été créée avec succès"

    def supprimer_categorie(self, label):
        """
        Supprime une catégorie existante à partir de son label.

        Cette méthode recherche une catégorie par son label dans la base de données. 
        Si elle la trouve, elle supprime cette catégorie et retourne un message 
        indiquant que la suppression a réussi. Si la catégorie n'est pas trouvée, 
        un message d'erreur est retourné.

        Parameters:
        - label (str): Le libellé de la catégorie à supprimer.

        Returns:
        str: Message indiquant le résultat de la suppression.

        Raises:
        ObjectDoesNotExist: Si la catégorie avec le libellé spécifié n'est pas trouvée.
        """
        try:
            categorie = Category.objects.get(label=label)
            categorie.delete()
            return f"Article avec le label {label} a été supprimé."
        except ObjectDoesNotExist:
            return f"Aucune catégorie trouvée avec le {label}."

    def modifier_label_categorie(self, categorie, nouveau_label):
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

        if not isinstance(categorie, Category):
            raise TypeError(
                "L'objet fourni n'est pas une instance de la classe Categorie.")
        try:
            existing_category = Category.objects.get(label=nouveau_label)
            return None
        except ObjectDoesNotExist:
            pass  # continuez le code si la catégorie n'existe pas

        setattr(categorie, "label", nouveau_label)
        setattr(categorie, "admin_id", self)
        categorie.save()
        return f"Le nouveau label {nouveau_label} a été appliqué à la catégorie"

    def modifier_appartenance_article(self, article, label_categorie):
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
        if not isinstance(article, Article):
            raise TypeError(
                "L'objet fourni n'est pas une instance de la classe Article.")
            return

        try:
            label_cat = Category.objects.get(label=label_categorie)
            article.cat = label_cat
            article.save()
            return f"{article.label} est à présent intégré dans la catégorie {label_categorie}"
        except ObjectDoesNotExist:
            return f"La catégorie {label_categorie} n'existe pas."

    def mettre_article_promotion(self, article, valeur_promo, start_date, end_date):
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
        # Vérification préalable

        if not isinstance(article, Article):
            raise TypeError(
                "L'objet fourni n'est pas une instance de la classe Article.")

        # Vérification de la validité des dates
        if start_date < datetime.now().date() or end_date < datetime.now().date():
            raise ObjectDoesNotExist(
                "La date de début ou de fin est dans le passé.")
        # Vérification de la plage
        if not (0 < valeur_promo < 80):
            raise ValueError(
                "La valeur de la promotion doit être comprise entre 0 et 80%")
        try:
            if article.promotion_valide(start_date, end_date):

                # Création de l'objet Article
                new_promotion = Promotion(
                    article=article,
                    percent=valeur_promo,
                    start_date=start_date,
                    end_date=end_date,
                    admin=self,  # L'administrateur qui crée l'article
                )
                new_promotion.save()
                return f"La promotion a été créée sur l'article {article.label} et débutera le {start_date} et prendra fin le {end_date}"
        except ObjectDoesNotExist:
            raise ObjectDoesNotExist(f"L'objet n'existe pas.")

    @staticmethod
    def supprimer_promotion(promotion_id):
        """
        Supprime une promotion existante à partir de son identifiant (ID).

        Cette méthode cherche une instance de la classe `Promotion` avec un identifiant donné
        et la supprime de la base de données si elle existe.

        Parameters:
        - promotion_id (int or str): L'identifiant unique de la promotion à supprimer.

        Returns:
        str: Un message indiquant si la suppression a réussi ou échoué.

        Raises:
        - ObjectDoesNotExist: Si aucune promotion n'est trouvée avec l'ID donné (géré silencieusement).
        """
        try:
            promotion = Promotion.objects.get(id=promotion_id)
            promotion.delete()
            return f"la promotion avec l'ID {promotion_id} a été supprimé."
        except ObjectDoesNotExist:
            return f"Aucune promotion n'a été trouvée avec l'ID {promotion_id}."

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
            promotions = Promotion.objects.all()
            # Recherche des promotions expirées
            for promotion in promotions:
                if date_du_jour > promotion.end_date:
                    promotion.delete()

        except ObjectDoesNotExist:
            raise ObjectDoesNotExist(
                f"Aucune promotion n'a été trouvée pour être purgée.")


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
    admin = models.ForeignKey(
        "Administrator", null=True, on_delete=models.SET_NULL)

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
        "Administrator", null=True, on_delete=models.SET_NULL)
    cat = models.ForeignKey("Category", null=True, on_delete=models.SET_NULL)

    def retourner_prix(self):
        pass

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

    def promotion_valide(self, strt_date, ed_date):
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
    admin = models.ForeignKey("Administrator", on_delete=models.CASCADE)
