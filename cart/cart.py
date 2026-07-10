from decimal import Decimal
from catalog.models import Product

class SessionCart:
    """Корзина на основе Django-сессий"""

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def remove_unavailable(self, request=None):
        """Удаляет недоступные товары, возвращает список их названий."""
        product_ids = list(self.cart.keys())
        if not product_ids:
            return []
        available_ids = {
            str(p.id)
            for p in Product.objects.filter(id__in=product_ids, available=True)
        }
        removed_names = []
        for pid in list(self.cart.keys()):
            if pid not in available_ids:
                try:
                    product = Product.objects.get(id=int(pid))
                    removed_names.append(product.name)
                except Product.DoesNotExist:
                    removed_names.append('Товар удалён')
                del self.cart[pid]
        if removed_names:
            self.save()
        return removed_names

    def add(self, product, quantity=1):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}
        self.cart[product_id]['quantity'] += quantity
        self.save()

    def update(self, product, quantity):
        product_id = str(product.id)
        if product_id in self.cart:
            if quantity > 0:
                self.cart[product_id]['quantity'] = quantity
            else:
                self.remove(product)
            self.save()

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def clear(self):
        del self.session['cart']
        self.session.modified = True

    def save(self):
        self.session.modified = True

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product'] = product
        for item in cart.values():
            if 'product' not in item:
                continue
            item['total_price'] = Decimal(item['price']) * item['quantity']
            yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(
            Decimal(item['price']) * item['quantity']
            for item in self.cart.values()
        )
