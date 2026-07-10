from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

from catalog.models import Product

from .cart import SessionCart
from .models import Cart, CartItem


@receiver(user_logged_in)
def load_cart_on_login(sender, request, user, **kwargs):
    """При входе: сливаем сессионную корзину с корзиной из БД,
    результат загружаем обратно в сессию."""
    session_cart = SessionCart(request)
    db_cart, _ = Cart.objects.get_or_create(user=user)

    # Сохраняем копию сессионных позиций до очистки
    session_items = dict(session_cart.cart)

    # Переносим позиции из сессии в БД
    for product_id, data in session_items.items():
        try:
            product = Product.objects.get(id=int(product_id), available=True)
        except Product.DoesNotExist:
            continue
        cart_item, created = CartItem.objects.get_or_create(
            cart=db_cart,
            product=product,
            defaults={'quantity': data['quantity']},
        )
        if not created:
            cart_item.quantity += data['quantity']
            cart_item.save()

    # Очищаем сессию и напрямую записываем актуальное состояние из БД
    session_cart.clear()
    new_cart = {}
    for item in db_cart.items.select_related('product').all():
        new_cart[str(item.product.id)] = {
            'quantity': item.quantity,
            'price': str(item.product.price),
        }
    request.session['cart'] = new_cart
    request.session.modified = True


@receiver(user_logged_out)
def save_cart_on_logout(sender, request, user, **kwargs):
    """При выходе: сохраняем сессионную корзину в БД и очищаем сессию."""
    if user is None:
        return
    try:
        db_cart = Cart.objects.get(user=user)
        db_cart.clear()
        session_cart = SessionCart(request)
        session_items = dict(session_cart.cart)
        for product_id, data in session_items.items():
            try:
                product = Product.objects.get(
                    id=int(product_id), available=True
                )
            except Product.DoesNotExist:
                continue
            CartItem.objects.create(
                cart=db_cart,
                product=product,
                quantity=data['quantity'],
            )
        session_cart.clear()
    except Cart.DoesNotExist:
        pass