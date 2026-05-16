from django.urls import path

from . import views

urlpatterns = [
    path('', views.catalog, name='catalog'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
]
