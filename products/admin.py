from django.contrib import admin
from django import forms
from .models import Product, Offer, Category
from accounts.models import Cart, Order
from accounts.admin import custom_admin_site  # Import your custom admin.site


class ProductInline(admin.TabularInline):
    model = Product
    extra = 1 # Allows adding products from Category panel


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductInline] # Shows products inside categories

class OfferAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount')

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'category': admin.widgets.FilteredSelectMultiple("Category", is_stacked=False),
        }


class ProductAdmin(admin.ModelAdmin):
    form = ProductForm
    list_display = ('name', 'price', 'stock', 'category')
    list_filter = ('category',)
    search_fields = ('name', 'category__name')



custom_admin_site.register(Product, ProductAdmin)
custom_admin_site.register(Category, CategoryAdmin)
custom_admin_site.register(Offer, OfferAdmin)

# Modify the Django Admin Panel branding
# admin.site.site_header = "PyShop Admin"
# admin.site.site_title = "PyShop Admin Panel"
# admin.site.index_title = "Manage PyShop"

