from django.contrib.auth.models import User
from django.test import TestCase


class AuthTests(TestCase):
    """Тесты 1-2: регистрация и вход"""

    def test_registration_creates_user_and_redirects(self):
        response = self.client.post('/register/', {
            'username': 'newuser',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
        })
        self.assertRedirects(response, '/')
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login_authenticates_and_redirects(self):
        User.objects.create_user(username='testuser', password='TestPass123!')
        response = self.client.post('/login/', {
            'username': 'testuser',
            'password': 'TestPass123!',
        })
        self.assertRedirects(response, '/')
        follow_response = self.client.get('/')
        self.assertTrue(follow_response.wsgi_request.user.is_authenticated)


class AdminTests(TestCase):
    """Тест 10: смена статуса заказа администратором"""

    def setUp(self):
        from orders.models import Order
        self.admin = User.objects.create_superuser(username='admin', password='AdminPass123!')
        self.user = User.objects.create_user(username='buyer', password='TestPass123!')
        self.order = Order.objects.create(
            user=self.user,
            first_name='Иван', last_name='Иванов',
            address='ул. Ленина, 1', status='created',
        )

    def test_admin_changes_order_status_visible_in_order_list(self):
        self.client.login(username='admin', password='AdminPass123!')
        self.client.post(
            f'/admin/orders/order/{self.order.id}/change/',
            {
                'status': 'paid',
                'user': self.user.id,
                'first_name': 'Иван',
                'last_name': 'Иванов',
                'address': 'ул. Ленина, 1',
                'items-TOTAL_FORMS': '0',
                'items-INITIAL_FORMS': '0',
                'items-MIN_NUM_FORMS': '0',
                'items-MAX_NUM_FORMS': '1000',
                '_save': 'Сохранить',
            },
        )
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'paid')
        self.client.login(username='buyer', password='TestPass123!')
        response = self.client.get('/orders/')
        self.assertContains(response, 'Оплачен')
