from django.test import TestCase

from catalog.models import Category, Product


class CartTests(TestCase):
    """Тесты 6-7: корзина"""

    def setUp(self):
        category = Category.objects.create(name='Тест', slug='test')
        self.product = Product.objects.create(
            name='Товар', slug='tovar',
            category=category, price=500, available=True,
        )

    def test_add_product_to_cart(self):
        self.client.post(f'/cart/add/{self.product.id}/')
        session = self.client.session
        self.assertIn(str(self.product.id), session.get('cart', {}))

    def test_update_cart_quantity_recalculates_total(self):
        self.client.post(f'/cart/add/{self.product.id}/')
        self.client.post(f'/cart/update/{self.product.id}/', {'quantity': 3})
        session = self.client.session
        self.assertEqual(session['cart'][str(self.product.id)]['quantity'], 3)
        response = self.client.get('/cart/')
        self.assertContains(response, '1500')

    def test_remove_product_from_cart(self):
        self.client.post(f'/cart/add/{self.product.id}/')
        self.client.post(f'/cart/remove/{self.product.id}/')
        session = self.client.session
        self.assertNotIn(str(self.product.id), session.get('cart', {}))
