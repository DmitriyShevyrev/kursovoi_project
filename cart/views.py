from django.shortcuts import get_object_or_404, redirect, render
from catalog.models import Product
from .cart import SessionCart
from django.contrib import messages

def cart_detail(request):
    cart = SessionCart(request)
    return render(request, 'cart/cart.html', {'cart': cart})


def cart_add(request, product_id):
    cart = SessionCart(request)
    product = get_object_or_404(Product, id=product_id, available=True)
    if request.method == 'POST':
        cart.add(product=product)
    return redirect('cart_detail')


def cart_remove(request, product_id):
    if request.method != 'POST':
        return redirect('cart_detail')
    cart = SessionCart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart_detail')


def cart_update(request, product_id):
    cart = SessionCart(request)
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 1))
        except (ValueError, TypeError):
            quantity = 1
        quantity = max(1, min(quantity, 99))
        cart.update(product=product, quantity=quantity)
    return redirect('cart_detail')


def cart_clear(request):
    if request.method == 'POST':
        SessionCart(request).clear()
    return redirect('cart_detail')

def cart_detail(request):
    cart = SessionCart(request)
    removed = cart.remove_unavailable(request)
    if removed:
        for name in removed:
            messages.warning(
                request,
                f'Товар «{name}» был удалён из корзины, так как стал недоступен.'
            )
    return render(request, 'cart/cart.html', {'cart': cart})