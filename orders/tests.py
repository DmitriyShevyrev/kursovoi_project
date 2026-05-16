from django.contrib.auth.models import User
from django.test import TestCase

from catalog.models import Category, Product

from .models import Order


class OrderTests(TestCase):
    """Тесты 8-9: оформление заказа и история"""

    def setUp(self):
        self.user = User.objects.create_user(username='buyer', password='TestPass123!')
        category = Category.objects.create(name='Тест', slug='test')
        self.product = Product.objects.create(
            name='Товар', slug='tovar',
            category=category, price=500, available=True,
        )

    def test_create_order_clears_cart_and_sets_status(self):
        self.client.login(username='buyer', password='TestPass123!')
        self.client.post(f'/cart/add/{self.product.id}/')
        response = self.client.post('/orders/create/', {
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'address': 'ул. Ленина, 1',
        })
        order = Order.objects.filter(user=self.user).first()
        self.assertIsNotNone(order)
        self.assertEqual(order.status, 'created')
        self.assertEqual(order.items.count(), 1)
        self.assertNotIn('cart', self.client.session)
        self.assertRedirects(response, f'/orders/{order.id}/')

    def test_order_list_shows_user_orders(self):
        Order.objects.create(
            user=self.user,
            first_name='Иван', last_name='Иванов',
            address='ул. Ленина, 1', status='created',
        )
        self.client.login(username='buyer', password='TestPass123!')
        response = self.client.get('/orders/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Создан')

    def test_order_cancel(self):
        self.client.login(username='buyer', password='TestPass123!')
        order = Order.objects.create(
            user=self.user,
            first_name='Иван', last_name='Иванов',
            address='ул. Ленина, 1', status='created',
        )
        self.client.post(f'/orders/{order.id}/cancel/')
        order.refresh_from_db()
        self.assertEqual(order.status, 'cancelled')
