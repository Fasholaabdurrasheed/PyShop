from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Cart, Order, OrderItem
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth.admin import UserAdmin, GroupAdmin


# === Custom Admin Site ===
class CustomAdminSite(admin.AdminSite):
    site_header = "PyShop Admin"
    site_title = "PyShop Admin Portal"
    index_title = "Welcome to the PyShop Dashboard"

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['custom_dashboard_link'] = reverse('admin-dashboard')  # optional custom link
        return super().index(request, extra_context=extra_context)


custom_admin_site = CustomAdminSite(name='custom_admin')


# === Cart Admin ===
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'total_items', 'cart_total_price')
    search_fields = ('user__username',)

    def total_items(self, obj):
        return obj.items.count()
    total_items.short_description = 'Total Items'

    def cart_total_price(self, obj):
        return f"₦{obj.total_price:,.2f}"
    cart_total_price.short_description = 'Total Price'

# === Order Admin ===
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'payment_method', 'is_paid', 'is_verified')
    list_filter = ('payment_method', 'is_paid', 'is_verified')
    search_fields = ('user__username', 'id')
    actions = ['mark_as_verified']

    def mark_as_verified(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f"{updated} orders marked as verified.")
    mark_as_verified.short_description = "Mark selected orders as verified"


# === Register your models to the custom admin site ===
custom_admin_site.register(Cart, CartAdmin)
custom_admin_site.register(Order, OrderAdmin)
custom_admin_site.register(OrderItem)

# === Register Django built-in auth models ===
custom_admin_site.register(User, UserAdmin)
custom_admin_site.register(Group, GroupAdmin)
custom_admin_site.register(Permission)
