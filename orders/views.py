from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from cart.cart import SessionCart
from users.models import Profile

from .forms import OrderCreateForm
from .models import Order, OrderItem


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
            return redirect('order_detail', order_id=order.id)
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
    if request.method == 'POST' and order.can_cancel():
        order.status = 'cancelled'
        order.save()
    return redirect('order_detail', order_id=order.id)
