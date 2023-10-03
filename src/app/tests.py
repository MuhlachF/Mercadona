from .models import Article, Category, User
from django.test import TestCase, Client
from django.core.exceptions import ObjectDoesNotExist, FieldError
from app.models import Article, Category, Promotion
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
            price=Decimal(2600),
            category=self.categorie,
            admin=self.user  # Utilisation de l'utilisateur créé
        )

        # Création de dates pour les tests
        self.date_now = date(2023, 10, 3)
        self.date_start_avant_now = date(2021, 1, 1)
        self.date_start_valide = date(2024, 2, 1)
        self.date_end_avant_start = date(2023, 12, 1)
        self.date_end_avant_now = date(2023, 9, 1)
        self.date_end_valide = date(2024, 3, 1)

        self.date_start_promotion_1 = date(2023, 9, 1)
        self.date_end_promotion_1 = date(2023, 12, 31)
        self.date_start_recouvrement = date(2023, 10, 1)
        self.date_end_recouvrement = date(2023, 10, 1)
        self.date_start_promotion_OK = date(2024, 1, 1)
        self.date_fin_promotion_OK = date(2024, 2, 1)

        self.date_debut_promotion_valide = date(2023, 10, 1)
        self.date_fin_promotion_valide = date(2024, 10, 1)
        self.date_debut_promotion_depassee = date(2022, 10, 1)
        self.date_fin_promotion_depassee = date(2022, 12, 31)

        # Création de promotions
        self.promotion_1 = Promotion.objects.create(
            start_date=self.date_start_promotion_1, end_date=self.date_end_promotion_1, percent=40, article=self.article)

        # Création d'une promotion valide pour l'article 2
        self.promotion_2 = Promotion.objects.create(
            start_date=self.date_debut_promotion_valide, end_date=self.date_fin_promotion_valide, percent=40, article=self.article_2)

        # Création d'une promotion non valide pour l'article 3
        self.promotion_3 = Promotion.objects.create(
            start_date=self.date_debut_promotion_depassee, end_date=self.date_fin_promotion_depassee, percent=40, article=self.article_3)

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

    def test_promotion_est_valide_date_invalide(self):
        # Test pour vérifier le retour de la fonction pour une date de fin antérieure à la date de début
        message = self.article.promotion_est_valide(
            self.date_start_valide, self.date_end_avant_start)
        self.assertEqual(message, False)

    def test_promotion_est_valide_date_invalide_2(self):
        # Test pour vérifier le retour de la fonction pour une date de fin de fin antérieure à la date actuelle
        message = self.article.promotion_est_valide(
            self.date_start_avant_now, self.date_end_avant_now)
        self.assertEqual(message, False)

    def test_promotion_est_valide_promotion_existante(self):
        # Test pour vérifier le retour de la fonction pour une promotion renseignée sur la période de la promotion existante
        message = self.article.promotion_est_valide(
            self.date_start_recouvrement, self.date_end_recouvrement)
        self.assertEqual(message, False)

    def test_promotion_est_valide_promotion_existante_date_debut_uniquement(self):
        # Test pour vérifier le retour de la fonction pour une promotion renseignée sur la période de la promotion existante
        message = self.article.promotion_est_valide(
            self.date_start_recouvrement, self.date_fin_promotion_OK)
        self.assertEqual(message, False)

    def test_promotion_est_valide_promotion_valide(self):
        # Test pour vérifier le retour de la fonction pour une promotion renseignée sur la période de la promotion existante
        message = self.article.promotion_est_valide(
            self.date_start_promotion_OK, self.date_fin_promotion_OK)
        self.assertEqual(message, True)

    # Véricication de la validité de la période de promotion
    def test_tester_validation_promotion_2(self):
        message = self.article_2.promotion_en_cours()
        self.assertEqual(message, 40)

    # Véricication de la non validité de la période de promotion
    def test_tester_validation_promotion_3(self):
        message = self.article_3.promotion_en_cours()
        self.assertEqual(message, 0)

    # Véricication du prix d'un article en promotion
    def test_tester_prix_article_promotion(self):
        self.assertEqual(self.article_2.retourner_prix(), Decimal(
            1560.47).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP))

        # Véricication du prix d'un article qui n'est pas en promotion
    def test_tester_prix_article_hors_promotion(self):
        self.assertEqual(self.article_3.retourner_prix(), Decimal(
            2600).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP))


class TestModelePromotion(TestCase):

    def setUp(self):
        # Création des dates
        self.date_start_promotion = date(2024, 1, 1)
        self.date_fin_promotion = date(2024, 2, 1)

        # Création d'une catégorie
        self.categorie = Category.objects.create(label='Electronique')

        # Création d'un article
        self.article = Article.objects.create(
            label='Ordinateur',
            description='Un ordinateur puissant',
            price=999.99,
            category=self.categorie
        )

    def test_creer_promotion(self):
        # Test de la création d'une nouvelle promotion
        promotion = Promotion.objects.create(
            start_date=self.date_start_promotion, end_date=self.date_fin_promotion, percent=40, article=self.article)

        self.assertEqual(Promotion.objects.count(), 1)
        self.assertEqual(promotion.start_date, self.date_start_promotion)
