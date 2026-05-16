from decimal import Decimal

from django.conf import settings
from django.db import models

from catalog.models import Product


class Cart(models.Model):
    """Персистентная корзина авторизованного пользователя.

    Основное взаимодействие с корзиной идёт через сессии (см. cart.cart.SessionCart),
    а эта модель хранит сохранённое состояние корзины между сеансами.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Пользователь',
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

    def __str__(self):
        return f'Корзина {self.user.username}'

    def get_total_price(self):
        return sum((item.get_total_price() for item in self.items.all()), Decimal('0'))

    def clear(self):
        self.items.all().delete()


class CartItem(models.Model):
    """Позиция в персистентной корзине"""
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Корзина',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Товар',
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')
    added = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Позиция корзины'
        verbose_name_plural = 'Позиции корзины'
        unique_together = ('cart', 'product')

    def __str__(self):
        return f'{self.product.name} x{self.quantity}'

    def get_total_price(self):
        return self.product.price * self.quantity
