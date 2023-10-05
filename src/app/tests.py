from .models import Article, Category, User
from django.test import TestCase, Client
from django.core.exceptions import ObjectDoesNotExist, FieldError, ValidationError
from app.models import Article, Category, Promotion
from app.admin import ArticleForm, CategoryForm, PromotionForm
from datetime import date, datetime, timedelta
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
        self.date_fin_promotion_valide = date(2024, 10, 1)
        self.date_du_jour = date.today()

        # Dates valides de promotion - série 2 - recouvrement de plage
        self.date_fin_promotion_valide_recouvrement = date(2024, 5, 1)

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

    def test_dates_valides_recouvrement_promotion_(self):
        # Test Création d'une promotion valide mais sur une promotion
        # existante en cours et valide

        self.promotion_3 = Promotion.objects.create(
            start_date=self.date_du_jour, end_date=self.date_fin_promotion_valide,
            percent=25, article=self.article_2)

        with self.assertRaises(ValidationError):
            self.promotion_4 = Promotion.objects.create(
                start_date=self.date_du_jour, end_date=self.date_fin_promotion_valide_recouvrement,
                percent=25, article=self.article_2)


class ArticleFormTest(TestCase):

    def test_form_valid(self):
        # Test portant sur la validité du formulaire si la saisie est effectuée à minima
        category = Category.objects.create(label='Electronics')
        user = User.objects.create_user(
            username='testuser', password='testpass')
        form_data = {
            'label': 'PC',
            'price': '10.00',
            'category': category.id,
            'admin': user.id,
        }
        form = ArticleForm(form_data)

        self.assertTrue(form.is_valid())

    def test_clean_price_invalid(self):
        # Test si un prix inférieur à 0 est renseigné
        category = Category.objects.create(label='Electronics')
        user = User.objects.create_user(
            username='testuser', password='testpass')
        form_data = {
            'label': 'PC',
            'price': '-10.00',
            'category': category.id,
            'admin': user.id,
        }
        form = ArticleForm(form_data)

        self.assertFalse(form.is_valid())

    def test_clean_price_non_decimal(self):
        # Test si une chaine de caratères est renseignées à la place d'un prix
        category = Category.objects.create(label='Electronics')
        user = User.objects.create_user(
            username='testuser', password='testpass')
        form_data = {
            'label': 'PC',
            'price': 'abc',
            'category': category.id,
            'admin': user.id,
        }
        form = ArticleForm(form_data)
        self.assertFalse(form.is_valid())

    def test_clean_label_non_rensigne(self):
        # Test si le label n'est pas rensigné
        category = Category.objects.create(label='Electronics')
        user = User.objects.create_user(
            username='testuser', password='testpass')
        form_data = {
            'price': 'abc',
            'category': category.id,
            'admin': user.id,
        }
        form = ArticleForm(form_data)
        self.assertFalse(form.is_valid())

    def test_clean_categorie_non_rensignee(self):
        # Test si le label n'est pas rensigné
        category = Category.objects.create(label='Electronics')
        user = User.objects.create_user(
            username='testuser', password='testpass')
        form_data = {
            'label': 'PC',
            'price': 'abc',
            'admin': user.id,
        }
        form = ArticleForm(form_data)
        self.assertFalse(form.is_valid())


class CategoryFormTest(TestCase):
    def test_category_form_valid(self):
        form = CategoryForm({'label': 'Electronics'})
        self.assertTrue(form.is_valid())


class PromotionFormTest(TestCase):

    def test_clean_valid(self):
        # Test si la promotion saisie est postérieure à la date du jour
        form = PromotionForm({
            'start_date': datetime.now().date(),
            'end_date': datetime.now().date() + timedelta(days=1),
            'percent': '10',
            'article': Article.objects.create(label='Test', price=Decimal('10.00'))
        })
        self.assertTrue(form.is_valid())

    def test_clean_invalid_dates(self):
        # Test si la date de fin est antiérieure à la date de début
        form = PromotionForm({
            'start_date': datetime.now().date() + timedelta(days=1),
            'end_date': datetime.now().date(),
            'percent': '10',
            'article': Article.objects.create(label='Test', price=Decimal('10.00'))
        })
        self.assertFalse(form.is_valid())

    def test_clean_invalid_percent(self):
        # Test si la promotion saisie est supérieure à 60%
        form = PromotionForm({
            'start_date': datetime.now().date(),
            'end_date': datetime.now().date() + timedelta(days=1),
            'percent': '60',
            'article': Article.objects.create(label='Test', price=Decimal('10.00'))
        })
        self.assertFalse(form.is_valid())

    def test_clean_invalid_percent_2(self):
        # Test si la promotion saisie est inférieure à 0
        form = PromotionForm({
            'start_date': datetime.now().date(),
            'end_date': datetime.now().date() + timedelta(days=1),
            'percent': '60',
            'article': Article.objects.create(label='Test', price=Decimal('10.00'))
        })
        self.assertFalse(form.is_valid())

    def test_clean_invalid_article(self):
        # Test si aucun article n'est sélectionné
        form = PromotionForm({
            'start_date': datetime.now().date(),
            'end_date': datetime.now().date() + timedelta(days=1),
            'percent': '0',
            'article': None
        })
        self.assertFalse(form.is_valid())
