from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from .models import Category, Product


def catalog(request):
    products = Product.objects.filter(available=True)
    categories = Category.objects.all()

    category_slug = request.GET.get('category')
    current_category = None
    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=current_category)

    query = request.GET.get('q')
    if query:
        products = products.filter(name__icontains=query)

    paginator = Paginator(products, 6)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'catalog/catalog.html', {
        'page_obj': page_obj,
        'categories': categories,
        'current_category': current_category,
        'query': query,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    return render(request, 'catalog/product_detail.html', {'product': product})
