from django.conf import settings
from django.template.context_processors import static
from django.conf.urls.static import static
from django.urls import path
from . import views
from .views import product_list, payment_success, order_confirmation, remove_from_cart, home

urlpatterns = [
    path('', home, name='home'),  # Homepage
    path('products/', product_list, name='product_list'),  # Product listing
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),  # Product details
    path('products/offer/', views.index, name='offer'),  # Offers Page

    # 🛒 Cart URLs
    path('cart/', views.cart_view, name='cart_view'),  # View cart
    path("products/cart/add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),  # Add to cart
    path("products/cart/remove/<int:product_id>/", remove_from_cart, name="remove_from_cart"),  # Remove from cart
    path('update_cart/<int:product_id>', views.update_cart, name='update_cart'),

    # ✅ Checkout & Payments
    path('checkout/', views.checkout, name='checkout'),  # Checkout page
    path('payment-success/', payment_success, name='payment_success'),  # Payment success page
    path('order_confirmation/<int:order_id>/', order_confirmation, name='order_confirmation'),  # Order confirmation
    path('admin/review-bank-transfers/', views.review_bank_transfers, name='review_bank_transfers'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
