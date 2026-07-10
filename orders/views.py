import logging

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from cart.cart import SessionCart
from users.models import Profile

from .forms import OrderCreateForm
from .models import Order, OrderItem

# __name__ здесь равен 'orders.views', поэтому логгер попадает
# под правило 'orders' из настроек LOGGING.
logger = logging.getLogger(__name__)


@login_required(login_url='/login/')
def order_create(request):
    cart = SessionCart(request)

    if len(cart) == 0:
        return redirect('catalog')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = Order.objects.create(
                user=request.user,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                address=form.cleaned_data['address'],
            )
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity'],
                )
            cart.clear()
            # Пишем идентификаторы, а не ФИО и адрес из формы: лог не должен
            # содержать персональные данные.
            logger.info(
                'Заказ создан: order_id=%s user_id=%s позиций=%s сумма=%s',
                order.id, request.user.id, order.items.count(), order.get_total_price(),
            )
            return redirect('order_detail', order_id=order.id)
        else:
            # Какие поля не прошли валидацию — знать полезно, а вот что
            # именно ввёл пользователь, в лог не попадает.
            logger.warning(
                'Форма заказа не прошла валидацию: user_id=%s поля=%s',
                request.user.id, list(form.errors.keys()),
            )
    else:
        profile, _ = Profile.objects.get_or_create(user=request.user)
        form = OrderCreateForm(initial={
            'first_name': profile.first_name,
            'last_name': profile.last_name,
            'address': profile.address,
        })

    return render(request, 'orders/order_create.html', {'cart': cart, 'form': form})


@login_required(login_url='/login/')
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})


@login_required(login_url='/login/')
def order_list(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required(login_url='/login/')
def order_cancel(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if request.method == 'POST':
        if order.can_cancel():
            previous_status = order.status
            order.status = 'cancelled'
            order.save()
            logger.info(
                'Заказ отменён: order_id=%s user_id=%s был_статус=%s',
                order.id, request.user.id, previous_status,
            )
        else:
            # Кнопку отмены шаблон прячет, но запрос можно отправить и напрямую.
            # Такие попытки стоит видеть: это либо ошибка в шаблоне, либо обход.
            logger.warning(
                'Отклонена отмена заказа: order_id=%s user_id=%s статус=%s',
                order.id, request.user.id, order.status,
            )
    return redirect('order_detail', order_id=order.id)
