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


class OrderLoggingTests(TestCase):
    """Логи заказа не должны содержать персональных данных.

    Требование проекта: ФИО, адреса и телефоны не покидают базу данных.
    Лог — такое же хранилище ПДн, но его легко скопировать или закоммитить,
    поэтому в него пишутся только идентификаторы (order_id, user_id).

    assertLogs перехватывает записи логгера 'orders' во время блока with
    и складывает их в cm.output — там мы их и проверяем.
    """

    def setUp(self):
        self.user = User.objects.create_user(username='buyer', password='TestPass123!')
        category = Category.objects.create(name='Тест', slug='test')
        self.product = Product.objects.create(
            name='Товар', slug='tovar',
            category=category, price=500, available=True,
        )
        self.client.login(username='buyer', password='TestPass123!')

    def test_order_log_has_ids_but_no_personal_data(self):
        self.client.post(f'/cart/add/{self.product.id}/')

        with self.assertLogs('orders', level='INFO') as cm:
            self.client.post('/orders/create/', {
                'first_name': 'Пётр',
                'last_name': 'Незабудкин',
                'address': 'г. Краснодар, ул. Секретная, д. 13',
            })

        log = '\n'.join(cm.output)
        order = Order.objects.filter(user=self.user).first()

        # Идентификаторы должны быть — иначе лог бесполезен.
        self.assertIn(f'order_id={order.id}', log)
        self.assertIn(f'user_id={self.user.id}', log)

        # А персональных данных быть не должно.
        for personal in ('Пётр', 'Незабудкин', 'Краснодар', 'Секретная'):
            self.assertNotIn(personal, log)

    def test_rejected_cancel_is_logged_as_warning(self):
        # Заказ уже уехал в доставку — отменить его нельзя.
        order = Order.objects.create(
            user=self.user,
            first_name='Пётр', last_name='Незабудкин',
            address='г. Краснодар, ул. Секретная, д. 13', status='shipped',
        )

        with self.assertLogs('orders', level='WARNING') as cm:
            self.client.post(f'/orders/{order.id}/cancel/')

        order.refresh_from_db()
        self.assertEqual(order.status, 'shipped')  # статус не изменился

        log = '\n'.join(cm.output)
        self.assertIn(f'order_id={order.id}', log)
        self.assertNotIn('Незабудкин', log)
