from django.test import TestCase

from .models import Category, Product


class CatalogTests(TestCase):
    """Тесты 3-5: каталог, поиск, карточка товара"""

    def setUp(self):
        self.category1 = Category.objects.create(name='Электроника', slug='electronics')
        self.category2 = Category.objects.create(name='Одежда', slug='clothes')
        self.product1 = Product.objects.create(
            name='Смартфон', slug='smartfon',
            description='Современный смартфон',
            category=self.category1, price=10000, available=True,
        )
        self.product2 = Product.objects.create(
            name='Куртка', slug='kurtka',
            description='Тёплая куртка',
            category=self.category2, price=5000, available=True,
        )

    def test_catalog_filters_by_category(self):
        response = self.client.get('/?category=electronics')
        self.assertContains(response, 'Смартфон')
        self.assertNotContains(response, 'Куртка')

    def test_catalog_search_by_keyword(self):
        response = self.client.get('/?q=Смарт')
        self.assertContains(response, 'Смартфон')
        self.assertNotContains(response, 'Куртка')

    def test_product_detail_shows_name_price_description(self):
        response = self.client.get('/product/smartfon/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Смартфон')
        self.assertContains(response, '10000')
        self.assertContains(response, 'Современный смартфон')


class FixtureTests(TestCase):
    """Проверка, что демо-каталог разворачивается из фикстуры.

    Django сам находит catalog.json в catalog/fixtures/ и загружает его
    в тестовую БД перед каждым тестом этого класса.

    Смысл теста: db.sqlite3 не хранится в репозитории, поэтому фикстура —
    единственный способ воспроизвести каталог после клонирования проекта.
    Если она сломается, мы узнаем об этом здесь, а не на защите.
    """
    fixtures = ['catalog.json']

    def test_fixture_restores_full_catalog(self):
        self.assertEqual(Category.objects.count(), 5)
        self.assertEqual(Product.objects.count(), 52)

    def test_fixture_keeps_descriptions_and_images(self):
        # Пустых описаний быть не должно: на них строится семантический поиск.
        self.assertEqual(Product.objects.filter(description='').count(), 0)
        self.assertEqual(Product.objects.filter(image='').count(), 0)

    def test_fixture_survives_non_ascii(self):
        # Символ «²» ломал выгрузку в кодировке Windows (cp1251).
        # Тест страхует от возврата этой ошибки при пересоздании фикстуры.
        self.assertTrue(
            Product.objects.filter(description__contains='²').exists()
        )
