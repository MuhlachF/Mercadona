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
        Article: L'objet Article nouvellement créé
        """

        # Valider les données en entrée
        if not label or not price:
            return None

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

        return new_article

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
        None

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

    def creer_categorie(self, label):
        """
        Crée une nouvelle catégorie dans la base de données.

        Cette méthode prend une chaîne de caractères pour le libellé de la catégorie, 
        crée une nouvelle instance de la classe Category avec ce libellé, et l'enregistre dans la base de données. 
        L'attribut 'admin' de la catégorie est également mis à jour pour référencer l'administrateur actuel.

        Parameters:
        - label (str): Le libellé de la nouvelle catégorie

        Returns:
        Category: La nouvelle instance de la catégorie créée, ou None si le label est vide.

        """
        # Valider les données en entrée
        if not label:
            return None

        # Création de l'objet catégorie
        new_category = Category(
            label=label,
            admin=self,  # L'administrateur qui crée la catégorie
        )
        new_category.save()

        return new_category

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

        Raises:
        TypeError: Si l'objet fourni n'est pas une instance de la classe `Categorie`.
        """
        if not isinstance(categorie, Category):
            raise TypeError(
                "L'objet fourni n'est pas une instance de la classe Categorie.")
        setattr(categorie, "label", nouveau_label)
        categorie.save()


class Category(models.Model):
    label = models.CharField(max_length=100, unique=True)
    admin = models.ForeignKey(
        "Administrator", null=True, on_delete=models.SET_NULL)


class Article(models.Model):
    label = models.CharField(max_length=100, blank=False, null=False)
    description = models.TextField(blank=True, default="")
    price = models.DecimalField(
        max_digits=6, decimal_places=2, blank=False, null=False)
    image = models.ImageField(blank=True, null=True)
    admin = models.ForeignKey(
        "Administrator", null=True, on_delete=models.SET_NULL)
    cat = models.ForeignKey("Category", null=True, on_delete=models.SET_NULL)

    def modifier_categorie(self, label_categorie):
        try:
            label_categorie = Category.objects.get(label=label_categorie)
            self.cat = label_categorie
            self.save()
        except ObjectDoesNotExist:
            return f"La catégorie {label_categorie} n'existe pas."


class Promotion(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()
    percent = models.DecimalField(max_digits=6, decimal_places=2)
    article = models.ForeignKey("Article", on_delete=models.CASCADE)
    admin = models.ForeignKey("Administrator", on_delete=models.CASCADE)
