from django.db import models
from django.core.exceptions import ObjectDoesNotExist, FieldError

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

        return f"L'article {label} au prix de {price} appartenant à la categorie {category} a été créé"

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
                print(f"{key} : {value}")
                modificiations_effectuees = True

            else:
                raise FieldError(f"Le champ {key} n'a pas été trouvé")

            if modificiations_effectuees:
                setattr(article, "admin", self)
                article.save()
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
            return f"La catégorie {existing_category} est déjà présente dans la base de données"
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

        try:
            label_cat = Category.objects.get(label=label_categorie)
            article.cat = label_cat
            article.save()
            return f"{article.label} est à présent intégré dans la catégorie {label_categorie}"
        except ObjectDoesNotExist:
            return f"La catégorie {label_categorie} n'existe pas."


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


class Promotion(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()
    percent = models.DecimalField(max_digits=6, decimal_places=2)
    article = models.ForeignKey("Article", on_delete=models.CASCADE)
    admin = models.ForeignKey("Administrator", on_delete=models.CASCADE)
