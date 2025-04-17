from csv import excel_tab
from itertools import product
import stripe
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import Cart, Order, OrderItem, CartItem
from .models import Product, Offer, Category
from .forms import BankTransferForm  # import the form
from django.core.mail import send_mail
from django.contrib.admin.views.decorators import staff_member_required
stripe.api_key = settings.STRIPE_SECRET_KEY


# 🚲 View Cart
#views.py

@login_required
def cart_view(request):
    cart = Cart.objects.filter(user=request.user).first()
    cart_items = cart.items.all() if cart else []

    total_price = sum(item.total_price for item in cart_items)  # Sum total prices for all cart items

    return render(request, "cart.html", {
        "cart_items": cart_items,
        "total_price": total_price
    })


# ➕ Add to Cart
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Ensure user has a cart (single cart per user)
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Ensure CartItem exists or create it
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        cart_item.quantity += 1  # Increment quantity if already in cart
        cart_item.save()

    # Ensure cart items are retrieved properly
    request.session.modified = True

    messages.success(request, f"{product.name} added to cart.")
    return redirect("cart_view")  # Redirect to cart view



# ❌ Remove from Cart
@login_required
def remove_from_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart.objects.filter(user=request.user).first()

    if cart:
        cart_item = CartItem.objects.filter(cart=cart, product=product).first()
        if cart_item:
            cart_item.delete()
            messages.success(request, "Item removed from cart.")
        else:
            messages.error(request, "Item not found in cart.")
    else:
        messages.error(request, "Cart not found.")

    return redirect("cart_view")


# ✅ Update Cart Quantity
@login_required
def update_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart.objects.filter(user=request.user).first()

    if cart:
        cart_item = CartItem.objects.filter(cart=cart, product=product).first()

        if cart_item and request.method == "POST":
            quantity = int(request.POST.get("quantity", 1))
            if quantity > 0:
                cart_item.quantity = quantity
                cart_item.save()
                messages.success(request, "Cart updated successfully.")
            else:
                cart_item.delete()
                messages.success(request, "Item removed from cart.")
        else:
            messages.error(request, "Item not found in cart.")
    else:
        messages.error(request, "Cart not found.")

    return redirect('cart_view')

# ✅ Checkout Process

@login_required
def checkout(request):
    cart = Cart.objects.get(user=request.user)
    cart_items = cart.items.all()

    if not cart_items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect("cart_view")

    total_price = sum(item.product.price * item.quantity for item in cart_items)

    if request.method == "POST":
        payment_method = request.POST.get("payment_method")
        address = request.POST.get("address")

        if not address:
            messages.error(request, "Please provide a shipping address.")
            return redirect("checkout")

        if payment_method == "bank_transfer":
            form = BankTransferForm(request.POST, request.FILES)
            if form.is_valid():
                # Create order with bank transfer details
                order = form.save(commit=False)
                order.user = request.user
                order.total_price = total_price
                order.status = "pending"
                order.payment_method = "bank_transfer"
                order.save()

                for cart_item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        quantity=cart_item.quantity,
                        price=cart_item.product.price,
                    )

                cart_items.delete()
                messages.success(request, "Order placed! Awaiting payment confirmation.")
                return redirect("order_confirmation", order_id=order.id)
            else:
                messages.error(request, "Please upload valid payment proof.")
                return redirect("checkout")

        else:  # Default to Stripe (card)
            stripe_token = request.POST.get("stripeToken")

            try:
                charge = stripe.Charge.create(
                    amount=int(total_price * 100),  # Convert to cents
                    currency="usd",
                    description=f"Order by {request.user.username}",
                    source=stripe_token,
                )

                order = Order.objects.create(
                    user=request.user,
                    total_price=total_price,
                    status="paid",
                    payment_method="paystack"  # or stripe/paystack label
                )

                for cart_item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        quantity=cart_item.quantity,
                        price=cart_item.product.price,
                    )

                cart_items.delete()
                messages.success(request, "Your order has been placed successfully!")
                return redirect("order_confirmation", order_id=order.id)

            except stripe.error.CardError as e:
                messages.error(request, f"Payment error: {str(e)}")
                return redirect("checkout")
    else:
        form = BankTransferForm()

    return render(request, "checkout.html", {
        "cart_items": cart_items,
        "total_price": total_price,
        "total_price_cent": int(total_price * 100),
        "stripe_public_key": settings.STRIPE_PUBLIC_KEY,
        "form": form,
        "shop_account_name": settings.SHOP_ACCOUNT_NAME,
        "shop_account_number": settings.SHOP_ACCOUNT_NUMBER,
        "shop_bank_name": settings.SHOP_BANK_NAME,
    })


# 🎯 Order Confirmation
@login_required
def order_confirmation(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        messages.error(request, "Sorry, that order could not be found.")
        return redirect('home')
    return render(request, "accounts/order_confirmation.html", {"order": order, "created_at": order.created_at})


# 🛆 Product Listing & Details
def index(request):
    products = Product.objects.all()
    return render(request, "index.html", {"products": products})


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, "products/product_detail.html", {"product": product})


def product_list(request):
    products = Product.objects.all()
    return render(request, "products/product_list.html", {"products": products})


# 🔎 Home Page with Search & Categories
def home(request):
    query = request.GET.get("q")
    category_id = request.GET.get("category")
    products = Product.objects.all()

    if query:
        products = products.filter(name__icontains=query)
    if category_id:
        products = products.filter(category_id=category_id)

    categories = Category.objects.all()
    return render(request, "home.html", {"products": products, "categories": categories})


# 🎉 Payment Success Page
def payment_success(request):
    return render(request, "payment_success.html")


@staff_member_required
def review_bank_transfers(request):
    pending_orders = Order.objects.filter(status='pending', payment_method='bank_transfer')

    if request.method == 'POST':
        action = request.POST.get('action')
        order_id = request.POST.get('order_id')
        order = get_object_or_404(Order, id=order_id)

        if action == 'is_verified':
            order.status = 'paid'
            order.save()

            # Send email to customer
            send_mail(
                subject='Payment Confirmed - PyShop',
                message=f'Dear {order.user.username},\n\nYour payment for Order #{order.id} has been confirmed. Thank you for shopping with PyShop!',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[order.user.email],
                fail_silently=False
            )
            messages.success(request, f"Order {order.id} approved and customer notified.")

        elif action == 'reject':
            order.status = 'cancelled'
            order.save()
            messages.warning(request, f"Order {order.id} marked as cancelled.")

        return redirect('review_bank_transfers')

    return render(request, 'admin/review_bank_transfers.html', {
        'pending_orders': pending_orders,
    })


