from app.models import Administrator, Category
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from django.core.exceptions import ObjectDoesNotExist, FieldError
from app.models import Administrator, Article, Category, Promotion
from datetime import datetime, timedelta


class AdministratorCreerArticleTestCase(TestCase):
    # Test - 1 : Tester la création d'un article avec toutes les informations nécessaires.
    # Test - 2 : Tester la création d'un article sans prix.
    # Test - 3 : Tester la création d'un article sans étiquette (label).
    # Test - 4 : Tester la création d'un article avec des informations supplémentaires comme une image et une description.

    def setUp(self):
        # Création de l'administrateur
        self.admin = Administrator.objects.create(
            name="Bob", last_name="Eponge", pseudo="Boby", email="bob@gmail.com", password="bob")
        self.category = Category.objects.create(label="Mobilier")

    def test_creer_article_complet(self):
        result = self.admin.creer_article(
            label="Chaise", price=50, description="Confortable", category=self.category)
        self.assertEqual(
            result, "L'article Chaise au prix de 50 €TTC appartenant à la categorie Mobilier a été créé")

        # Cérifier que l'article a été créé dans la base de données
        self.assertTrue(Article.objects.filter(label="Chaise").exists())

    def test_creer_article_sans_prix(self):
        result = self.admin.creer_article(label="Chaise", price=None)
        self.assertEqual(result, "Le prix ou l'étiquette n'est pas renseigné")

    def test_creer_article_sans_label(self):
        result = self.admin.creer_article(label=None, price=50)
        self.assertEqual(result, "Le prix ou l'étiquette n'est pas renseigné")

    def test_creer_article_supplementaire(self):
        result = self.admin.creer_article(
            label="Chaise", price=50, description="Confortable", image="chaise.jpg", category=self.category)
        self.assertEqual(
            result, "L'article Chaise au prix de 50 €TTC appartenant à la categorie Mobilier a été créé")

        # Vérifier également que l'article a été créé dans la base de données avec les détails supplémentaires
        article = Article.objects.get(label="Chaise")
        self.assertEqual(article.description, "Confortable")
        self.assertEqual(article.image, "chaise.jpg")


class AdministratorSupprimerArticleTestCase(TestCase):
    # Test - 1 : Un test qui vérifie que la méthode supprime un article existant et renvoie le bon message.
    # Test - 2 : Un test qui vérifie que la méthode gère correctement le cas où l'article n'existe pas.
    def setUp(self):
        self.admin = Administrator.objects.create(
            name="Bob", last_name="Eponge", pseudo="Boby", email="bob@gmail.com", password="bob"
        )
        self.category = Category.objects.create(label="Mobilier")
        self.article = Article.objects.create(
            label="Chaise", price=50, cat=self.category
        )

    def test_supprimer_article_existant(self):
        article_id = self.article.id
        result = self.admin.supprimer_article(article_id)
        self.assertEqual(
            result, f"Article avec l'ID {article_id} a été supprimé.")

        # Vérifier que l'article n'existe plus dans la base de données
        with self.assertRaises(ObjectDoesNotExist):
            Article.objects.get(id=article_id)

    def test_supprimer_article_inexistant(self):
        article_id = 9999  # Un ID qui n'existe pas dans la base de données
        result = self.admin.supprimer_article(article_id)
        self.assertEqual(
            result, f"Aucun article trouvé avec l'ID {article_id}.")

        # Vérifier que l'article n'existe toujours pas dans la base de données
        with self.assertRaises(ObjectDoesNotExist):
            Article.objects.get(id=article_id)


class AdministratorModifierArticleTestCase(TestCase):
    # Test - 1 : Un test qui modifie avec succès un attribut d'un article existant.
    # Test - 2 : Un test qui échoue lorsque l'objet fourni n'est pas une instance de Article.
    # Test - 3 : Un test qui échoue lorsqu'un champ inconnu est fourni.
    def setUp(self):
        self.admin = Administrator.objects.create(
            name="Bob", last_name="Eponge", pseudo="Boby", email="bob@gmail.com", password="bob")
        self.category = Category.objects.create(label="Mobilier")
        self.article = Article.objects.create(
            label="Chaise", price=50, admin=self.admin, cat=self.category)

    def test_modifier_article_avec_succes(self):
        new_price = 55.0
        new_label = "Nouvelle Chaise"
        result = self.admin.modifier_article(
            self.article, price=new_price, label=new_label)
        self.article.refresh_from_db()  # Rafraîchir l'objet depuis la base de données
        self.assertEqual(self.article.price, new_price)
        self.assertEqual(self.article.label, new_label)
        self.assertEqual(
            result, f"La modificiation de l'article {self.article} a été effectuée avec succès")

    def test_modifier_article_mauvais_type(self):
        with self.assertRaises(TypeError):
            self.admin.modifier_article(
                "ceci_n_est_pas_un_article", price=55.0)

    def test_modifier_article_champ_inconnu(self):
        with self.assertRaises(FieldError):
            self.admin.modifier_article(self.article, prix_inconnu=55.0)


class AdministratorCreerCategorieTestCase(TestCase):
    # Test-1 : La création réussie d'une nouvelle catégorie.
    # Test-2 : La tentative de création d'une catégorie sans libellé.
    # Test-3 : La tentative de création d'une catégorie qui existe déjà dans la base de données.

    def setUp(self):
        self.admin = Administrator.objects.create(
            name="Bob", last_name="Eponge", pseudo="Boby", email="bob@gmail.com", password="bob"
        )

    def test_creer_categorie_reussie(self):
        result = self.admin.creer_categorie(label="Electronique")
        self.assertEqual(
            result, "La catégorie Electronique a été créée avec succès")
        self.assertTrue(Category.objects.filter(label="Electronique").exists())

    def test_creer_categorie_sans_label(self):
        result = self.admin.creer_categorie(label=None)
        self.assertEqual(result, "Le label n'est pas renseigné")

    def test_creer_categorie_existante(self):
        Category.objects.create(label="Electronique", admin=self.admin)
        result = self.admin.creer_categorie(label="Electronique")
        self.assertEqual(
            result, "La catégorie Electronique est déjà présente dans la base de données")


class AdministratorSupprimerCategorieTestCase(TestCase):
    # Test-1 : La suppression réussie d'une catégorie existante.
    # Test-2 : La tentative de suppression d'une catégorie qui n'existe pas.
    def setUp(self):
        self.admin = Administrator.objects.create(
            name="Bob", last_name="Eponge", pseudo="Boby", email="bob@gmail.com", password="bob"
        )

    def test_creer_categorie_reussie(self):
        result = self.admin.creer_categorie(label="Electronique")
        self.assertEqual(
            result, "La catégorie Electronique a été créée avec succès")
        self.assertTrue(Category.objects.filter(label="Electronique").exists())

    def test_creer_categorie_sans_label(self):
        result = self.admin.creer_categorie(label=None)
        self.assertEqual(result, "Le label n'est pas renseigné")

    def test_creer_categorie_existante(self):
        Category.objects.create(label="Electronique", admin=self.admin)
        result = self.admin.creer_categorie(label="Electronique")
        self.assertEqual(
            result, "La catégorie Electronique est déjà présente dans la base de données")


class AdministratorModifierLabelCategorieTestCase(TestCase):
    # Test - 1 : Le changement de label réussi pour une catégorie existante.
    # Test - 2 : La tentative de modification avec un label déjà utilisé par une autre catégorie.
    # Test - 3 : Une erreur lorsque l'objet fourni n'est pas une instance de la classe Category.
    def setUp(self):
        self.admin = Administrator.objects.create(
            name="Bob", last_name="Eponge", pseudo="Boby", email="bob@gmail.com", password="bob"
        )
        self.category_electronique = Category.objects.create(
            label="Electronique", admin=self.admin)
        self.category_menage = Category.objects.create(
            label="Menage", admin=self.admin)

    def test_modifier_label_categorie_succes(self):
        result = self.admin.modifier_label_categorie(
            categorie=self.category_electronique, nouveau_label="Electro")
        self.assertEqual(
            result, "Le nouveau label Electro a été appliqué à la catégorie")
        self.category_electronique.refresh_from_db()
        self.assertEqual(self.category_electronique.label, "Electro")

    def test_modifier_label_categorie_label_existant(self):
        result = self.admin.modifier_label_categorie(
            categorie=self.category_electronique, nouveau_label="Menage")
        self.assertIsNone(result)

    def test_modifier_label_categorie_objet_incorrect(self):
        with self.assertRaises(TypeError):
            self.admin.modifier_label_categorie(
                categorie="NotACategory", nouveau_label="Electro")

    # ... (autres tests)


class AdministratorModifierAppartenanceArticleTestCase(TestCase):
    # Test - 1 : La modification réussie de la catégorie d'un article existant.
    # Test - 2 : Une erreur lorsqu'une catégorie inexistante est fournie.
    # Test - 3  :Une erreur lorsque l'objet fourni n'est pas une instance de la classe Article.
    def setUp(self):
        self.admin = Administrator.objects.create(
            name="John", last_name="Doe", pseudo="Johny", email="john@gmail.com", password="john"
        )
        self.category_electronics = Category.objects.create(
            label="Electronics", admin=self.admin)
        self.category_furniture = Category.objects.create(
            label="Furniture", admin=self.admin)
        self.article = Article.objects.create(
            label="Chair", price=45.0, cat=self.category_furniture, admin=self.admin)

    def test_modifier_appartenance_article_succes(self):
        result = self.admin.modifier_appartenance_article(
            self.article, "Electronics")
        self.assertEqual(
            result, f"{self.article.label} est à présent intégré dans la catégorie Electronics")
        self.article.refresh_from_db()
        self.assertEqual(self.article.cat.label, "Electronics")

    def test_modifier_appartenance_article_categorie_inexistante(self):
        result = self.admin.modifier_appartenance_article(
            self.article, "NonExistentCategory")
        self.assertEqual(
            result, f"La catégorie NonExistentCategory n'existe pas.")

    def test_modifier_appartenance_article_objet_incorrect(self):
        with self.assertRaises(TypeError):
            self.admin.modifier_appartenance_article(
                "NotAnArticle", "Electronics")


class AdministratorMettreArticlePromotionTestCase(TestCase):
    #  Test - 1 : Créer une promotion pour un article valide dans la plage de dates.
    #  Test - 2 : Essayer de créer une promotion pour un objet qui n'est pas un article.
    #  Test - 3 : Essayer de créer une promotion avec une valeur hors de la plage autorisée (0, 80).
    #  Test - 4 : Simuler un échec lors de la création de la promotion.
    def setUp(self):
        self.admin = Administrator.objects.create(
            name="Bob", last_name="Eponge", pseudo="Boby", email="bob@gmail.com", password="bob")
        self.category = Category.objects.create(label="Mobilier")
        self.article = Article.objects.create(
            label="Chaise", price=50, cat=self.category)

    def test_mettre_article_promotion_succes(self):
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=10)
        result = self.admin.mettre_article_promotion(
            self.article, 20, start_date, end_date)
        self.assertEqual(
            result, f"La promotion a été créée sur l'article {self.article.label} et débutera le {start_date} et prendra fin le {end_date}")

    def test_mettre_article_promotion_objet_incorrect(self):
        with self.assertRaises(TypeError):
            self.admin.mettre_article_promotion(
                "NotAnArticle", 20, datetime.now().date(), datetime.now().date())

    def test_mettre_article_promotion_valeur_incorrecte(self):
        with self.assertRaises(ValueError):
            self.admin.mettre_article_promotion(
                self.article, 90, datetime.now().date(), datetime.now().date())

    def test_mettre_article_promotion_creation_echec(self):
        with self.assertRaises(ObjectDoesNotExist):
            # Simulez une erreur ici, par exemple, en passant des dates invalides ou en manipulant la base de données
            self.admin.mettre_article_promotion(
                self.article, 20, datetime.now().date(), datetime.now().date())
