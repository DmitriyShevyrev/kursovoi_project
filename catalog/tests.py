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
