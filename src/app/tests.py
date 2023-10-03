from .models import Article, Category, User
from django.test import TestCase, Client
from django.core.exceptions import ObjectDoesNotExist, FieldError, ValidationError
from app.models import Article, Category, Promotion
from datetime import date
from django.contrib.auth import get_user_model
from decimal import Decimal, ROUND_HALF_UP

User = get_user_model()


class TestModeleCategorie(TestCase):

    def setUp(self):
        # Création de deux catégories, de deux articles et d'un utilisateur pour les tests
        self.categorie1 = Category.objects.create(label='Electronique')
        self.categorie2 = Category.objects.create(label='Mode')
        self.article1 = Article.objects.create(
            label='Ordinateur', category=self.categorie1, price=5.10)
        self.article2 = Article.objects.create(
            label='Chemise', category=self.categorie2, price=8)
        self.user = User.objects.create_user(
            username='mercadona', password='123456')

    def test_creer_categorie(self):
        # Test de la création d'une nouvelle catégorie
        categorie = Category.objects.create(label='Livres')
        self.assertEqual(Category.objects.count(), 3)
        self.assertEqual(categorie.label, 'Livres')

    def test_modifier_label_categorie(self):
        # Test de la modification du label d'une catégorie existante
        self.categorie1.modifier_label_categorie('Electronique et Gadgets')
        self.assertEqual(self.categorie1.label, 'Electronique et Gadgets')

    def test_lister_categories(self):
        # Test de la méthode qui liste toutes les catégories
        categories = Category.lister_categories()
        self.assertEqual(categories.count(), 2)
        self.assertIn(self.categorie1, categories)
        self.assertIn(self.categorie2, categories)

    def test_lister_articles_par_categorie(self):
        # Test de la méthode qui liste les articles d'une catégorie donnée
        articles = Category.lister_articles_categorie(
            label_categorie='Electronique')
        self.assertEqual(articles.count(), 1)
        self.assertIn(self.article1, articles)

        articles = Category.lister_articles_categorie('Mode')
        self.assertEqual(articles.count(), 1)
        self.assertIn(self.article2, articles)

    def test_lister_articles_par_categorie_inexistante(self):
        # Test de la méthode qui liste les articles d'une catégorie inexistante
        articles = Category.lister_articles_categorie('Inexistant')
        self.assertEqual(
            articles, "Aucune catégorie trouvée avec le label Inexistant.")


class TestModeleArticle(TestCase):

    def setUp(self):
        # Création d'un client pour simuler un utilisateur
        self.client = Client()

        # Création d'un utilisateur pour les tests
        self.user = User.objects.create_user(
            username='mercadona',
            password='123456'
        )

        # Simuler la connexion de l'utilisateur
        self.client.login(username='testuser', password='testpass')

        # Création d'une catégorie et de trois articles pour les tests
        self.categorie = Category.objects.create(label='Electronique')
        self.article = Article.objects.create(
            label='Smartphone',
            description='Un smartphone très intelligent',
            price=Decimal(599.99),
            category=self.categorie,
            admin=self.user  # Utilisation de l'utilisateur créé
        )

        self.article_2 = Article.objects.create(
            label='Smartphone',
            description='Un smartphone très intelligent',
            price=Decimal(2600.79),
            category=self.categorie,
            admin=self.user  # Utilisation de l'utilisateur créé
        )

        self.article_3 = Article.objects.create(
            label='PC',
            description='Un PC très performant',
            price=Decimal(2600.59),
            category=self.categorie,
            admin=self.user  # Utilisation de l'utilisateur créé
        )

        # Dates valides de promotion
        self.date_debut_promotion_valide = date(2024, 1, 1)
        self.date_fin_promotion_valide = date(2024, 10, 1)
        self.date_du_jour = date.today()

        # Création d'une promotion hors période
        self.promotion_1 = Promotion.objects.create(
            start_date=self.date_debut_promotion_valide, end_date=self.date_fin_promotion_valide, percent=40, article=self.article_2)

        # Création d'une promotion en cours
        self.promotion_2 = Promotion.objects.create(
            start_date=self.date_du_jour, end_date=self.date_fin_promotion_valide, percent=40, article=self.article_3)

    def test_creer_article(self):
        # Test de la création d'un nouvel article
        article = Article.objects.create(
            label='Ordinateur',
            description='Un ordinateur puissant',
            price=999.99,
            category=self.categorie
        )
        self.assertEqual(Article.objects.count(), 4)
        self.assertEqual(article.label, 'Ordinateur')

    def test_modifier_article(self):
        # Test de la modification d'un article existant
        message = self.article.modifier_article(user=self.user,
                                                label='Smartphone Pro', price=699.99)
        self.assertEqual(
            message, 'La modificiation de l\'article Smartphone Pro a été effectuée avec succès')
        self.assertEqual(self.article.label, 'Smartphone Pro')
        self.assertEqual(self.article.price, 699.99)

    def test_modifier_article_champ_inexistant(self):
        # Test de la modification d'un article avec un champ inexistant
        with self.assertRaises(FieldError):
            self.article.modifier_article(user=User, inexistant='Valeur')

    def test_modifier_categorie_article(self):
        # Test de la modification de la catégorie d'un article
        nouvelle_categorie = Category.objects.create(label='Informatique')
        message = self.article.modifier_categorie_article('Informatique')
        self.assertEqual(
            message, 'Smartphone est à présent intégré dans la catégorie Informatique')
        self.assertEqual(self.article.category, nouvelle_categorie)

    def test_modifier_categorie_article_inexistante(self):
        # Test de la modification de la catégorie d'un article avec une catégorie inexistante
        message = self.article.modifier_categorie_article('Inexistant')
        self.assertEqual(message, 'La catégorie Inexistant n\'existe pas.')

    def test_verifier_promotion_hors_periode_article(self):
        # test portant sur l'état d'une promotion non définie
        message = self.article_2.promotion_en_cours()
        self.assertEqual(message, Decimal(0))

    def test_verifier_promotion_non_renseignee_article(self):
        # test portant sur l'état d'une promotion valide
        message = self.article.promotion_en_cours()
        self.assertEqual(message, Decimal(0))

    def test_verifier_promotion_en_cours_article(self):
        # test portant sur l'état d'une promotion valide
        message = self.article_3.promotion_en_cours()
        self.assertEqual(message, Decimal(40.00))

    def test_recuperation_prix_article_en_promotion(self):
        # test portant sur la récupération d'un prix d'un article en promotion
        message = self.article_3.retourner_prix()
        self.assertEqual(message, Decimal(1560.35).quantize(
            Decimal('0.00'), rounding=ROUND_HALF_UP))

    def test_recuperation_prix_article_hors_promotion(self):
        # test portant sur la récupération d'un prix d'un article hors promotion
        message = self.article_2.retourner_prix()
        self.assertEqual(message, 'Aucune en cours')


class TestModelePromotion(TestCase):

    def setUp(self):
        # Dates valides de promotion
        self.date_debut_promotion_valide = date(2024, 1, 1)
        self.date_fin_promotion_valide = date(2024, 10, 1)
        self.date_du_jour = date.today()

        # Dates valides de promotion - série 2 - recouvrement de plage
        self.date_fin_promotion_valide_recouvrement = date(2024, 5, 1)

        # Dates non valides de promotion - date fin < date du jour
        self.date_debut_promotion_non_valide = date(2022, 1, 1)
        self.date_fin_promotion_non_valide = date(2022, 10, 1)

        # Dates non valides de promotion - inversion date de fin et date de début
        self.date_debut_promotion_inversion = date(2022, 10, 1)
        self.date_fin_promotion_inversion = date(2022, 1, 1)

        # Création d'une catégorie
        self.categorie = Category.objects.create(label='Electronique')

        # Création de 4 articles
        self.article = Article.objects.create(
            label='Ordinateur',
            description='Un ordinateur puissant',
            price=999.99,
            category=self.categorie
        )
        self.article_2 = Article.objects.create(
            label='Console',
            description='Une console incroyable',
            price=458.54,
            category=self.categorie
        )

        self.article_3 = Article.objects.create(
            label='Raspberry',
            description='Un petit ordi',
            price=258.50,
            category=self.categorie
        )

        self.article_4 = Article.objects.create(
            label='Arduino',
            description='Un micro controleur',
            price=28.50,
            category=self.categorie
        )

    def test_dates_non_valides_anterieures(self):
        # Test Création d'une promotion non valide - plage antérieure à la date du jour
        with self.assertRaises(ValidationError):
            self.promotion_1 = Promotion.objects.create(
                start_date=self.date_debut_promotion_non_valide, end_date=self.date_fin_promotion_non_valide, percent=40, article=self.article)

    def test_dates_non_valides_inversion(self):
        # Test Création d'une promotion non valide - date fin est antérieure à la date de début
        with self.assertRaises(ValidationError):
            self.promotion_1 = Promotion.objects.create(
                start_date=self.date_debut_promotion_inversion, end_date=self.date_fin_promotion_inversion, percent=40, article=self.article)

    def test_dates_non_valides_promotion_inferieure(self):
        # Test Création d'une promotion non valide - valeur promotion < 0
        with self.assertRaises(ValidationError):
            self.promotion_1 = Promotion.objects.create(
                start_date=self.date_debut_promotion_valide, end_date=self.date_fin_promotion_valide, percent=-5, article=self.article)

    def test_dates_non_valides_promotion_superieure_50(self):
        # Test Création d'une promotion non valide - valeur promotion < 0
        with self.assertRaises(ValidationError):
            self.promotion_1 = Promotion.objects.create(
                start_date=self.date_debut_promotion_valide, end_date=self.date_fin_promotion_valide, percent=55, article=self.article)

    def test_dates_valides_promotion_(self):
        # Test Création d'une promotion en cours et valide
        self.promotion_2 = Promotion.objects.create(
            start_date=self.date_du_jour, end_date=self.date_fin_promotion_valide, percent=25, article=self.article_2)
        message = self.article_2.promotion_en_cours()
        self.assertEqual(message, Decimal(25.00))

    def test_dates_valides_recouvrement_promotion_(self):
        # Test Création d'une promotion valide mais sur une promotion existante en cours et valide
        self.promotion_3 = Promotion.objects.create(
            start_date=self.date_du_jour, end_date=self.date_fin_promotion_valide, percent=25, article=self.article_2)

        with self.assertRaises(ValidationError):
            self.promotion_4 = Promotion.objects.create(
                start_date=self.date_du_jour, end_date=self.date_fin_promotion_valide_recouvrement, percent=25, article=self.article_2)
