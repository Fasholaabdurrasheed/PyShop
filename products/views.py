from itertools import product

from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Offer
from .cart import Cart

def index(request):
    products = Product.objects.all()
    return render(request, 'index.html',{'products': products})
def index2(request):
    offers = Offer.objects.all()
    return render(request, 'offer.html', {'offers': offers})
def add_to_cart(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.add(product)
    return redirect("cart_detail")
def remove_from_cart(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect("cart_detail")
def cart_detail(request):
    cart = Cart(request)
    return render(request, "cart_detail.html", {"cart": cart.get_items()})
def new(request):
    return HttpResponse('you are getting there InshAllah')