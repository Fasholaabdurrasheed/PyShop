from django.utils.timezone import now
from django.db import models
from django.contrib.auth.models import User
from products.models import Product

class Order(models.Model):
    PAYMENT_METHODS = [
        ('paystack', 'Paystack'),
        ('bank_transfer', 'Bank Transfer'),
    ]
    STATUS_CHOICE = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICE, default='pending')
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHODS, default='paystack')
    payment_proof = models.ImageField(upload_to='payment_proofs/', null=True, blank=True)
    transaction_note = models.TextField(null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False) # Admin will toggle this
    def __str__(self):
        return f"Order {self.id} - {self.user.username} - {self.status}"

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # One cart per user
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())  # using related_name='items'

    def __str__(self):
        return f"Cart of {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # ✅ Fixed: Added price field

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order {self.order.id})"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')  # Link to Cart
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_price(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in {self.cart.user.username}'s cart"
