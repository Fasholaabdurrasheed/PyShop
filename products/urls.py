from django.urls import path
from . import views
from .views import add_to_cart, remove_from_cart, cart_detail

urlpatterns = [
    path('',views.index),
    path('offer', views.index2),
    path("cart/add/<int:product_id>/", add_to_cart, name="add_to_cart"),
    path("cart/remove/<int:product_id>/", remove_from_cart, name="remove_from_cart"),
    path("cart/", cart_detail, name="cart_detail"),

]