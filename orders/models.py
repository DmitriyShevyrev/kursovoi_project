from django.conf import settings
from django.db import models

from catalog.models import Product


class Order(models.Model):
    """Заказ покупателя"""
    STATUS_CHOICES = [
        ('created', 'Создан'),
        ('paid', 'Оплачен'),
        ('shipped', 'Передан в доставку'),
        ('completed', 'Завершён'),
        ('cancelled', 'Отменён'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Покупатель',
    )
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    address = models.TextField(verbose_name='Адрес доставки')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='created',
        verbose_name='Статус',
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created']

    def __str__(self):
        return f'Заказ #{self.id} — {self.user.username}'

    def get_total_price(self):
        return sum(item.get_total_price() for item in self.items.all())

    def can_cancel(self):
        """Покупатель может отменить заказ, пока он не передан в доставку"""
        return self.status in ('created', 'paid')


class OrderItem(models.Model):
    """Позиция заказа — конкретный товар и его количество"""
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Заказ',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Товар',
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена на момент заказа')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'

    def __str__(self):
        return f'{self.product.name} x{self.quantity}'

    def get_total_price(self):
        return self.price * self.quantity
