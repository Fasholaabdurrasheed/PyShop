# from itertools import product

# from Demos.win32ts_logoff_disconnected import username
# from debugpy.common.util import  force_str
from django.utils.encoding import force_str
from django.contrib.auth.decorators import login_required
# from django.contrib.auth.password_validation import password_changed
# from django.http import HttpResponse
# from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
# from dns.e164 import query

from products.models import Product
from products.models import Category
from accounts.models import OrderItem, Cart
from .forms import RegisterForm
from .models import Order
from .email_utils import send_order_confirmation_email
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import smart_bytes
# from django.contrib.auth import get_user_model



# Create your views here.
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password']) # Hash password
            user.save()
            # Add success message
            messages.success(request, "Your account has been created successfully! check your mail for activation.")

            # Email verification setup
            current_site = get_current_site(request)
            mail_subject = "Activate your PyShop account"
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(smart_bytes(user.pk))
            verification_link = f"http://{current_site.domain}/accounts/activate/{uid}/{token}/"

            message = render_to_string('accounts/activation_email.html', {'user': user,'verification_link': verification_link})
            send_mail(mail_subject, message, 'abdulrasheedfashola@gmail.com',[user.email])

            return redirect('login') # Redirect to login page after registration
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home') # Redirect to homepage or dashboard
            else:
                messages.error(request, "Invalid username or password")
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('login') # Redirect to login page after logout
# views.py
from django.core.mail import send_mail
from django.http import HttpResponse
from django.conf import settings

def test_mail(request):
    try:
        send_mail(
            subject='Test Email from PyShop',
            message='This is a test email to check if sending works.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['rashfashkdp@gmail.com'],  # Replace with a test email
            fail_silently=False,
        )
        return HttpResponse("Test email sent successfully!")
    except Exception as e:
        return HttpResponse(f"Failed to send email: {str(e)}")
def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user =User.objects.get(pk=uid)
    except (TypeError, ValueError,OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user,token):
        user.is_active = True
        user.save()
        login(request, user)
        return HttpResponse("Your account has been activated successfully. You can now login.")
    else:
        return HttpResponse("Activation link is invalid or has expired.")


def home(request):
    query = request.GET.get('q')
    category_id = request.GET.get('category')

    products = Product.objects.all()

    if query:
        products = products.filter(name__icontains=query)
    if category_id:
        products = products.filter(category_id=category_id)

    categories = Category.objects.all()

    return render(request, 'home.html', {'products': products, 'categories': categories})


def email_verification_sent(request):
    return render(request, 'accounts/email_verification_sent.html')

from django.core.mail import send_mail

def mark_as_verified(self, request, queryset):
    for order in queryset:
        order.is_verified = True
        order.save()
        send_mail(
            'Payment Verified - PyShop',
            f'Hello {order.user.username},\n\nYour payment for order #{order.id} has been verified.',
            'abdulrasheedfashola@gmail.com',
            [order.user.email],
            fail_silently=True,
        )
    self.message_user(request, f"{queryset.count()} orders verified and customers notified.")
# accounts/views.py
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum
from django.utils.timezone import now, timedelta

@staff_member_required
def admin_dashboard(request):
    from django.core.mail import send_mail  # You already imported it above, so this can stay or move up
    from django.conf import settings

    # Handle form submission
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        is_paid = request.POST.get('is_paid') == 'on'
        is_verified = request.POST.get('is_verified') == 'on'

        try:
            order = Order.objects.get(id=order_id)
            order.is_paid = is_paid
            order.is_verified = is_verified
            order.save()

            # Send confirmation email if paid is True
            if is_paid:
                send_mail(
                    subject='Payment Confirmed - PyShop',
                    message=f'Hello {order.user.username},\n\nYour payment for Order #{order.id} has been confirmed. Thank you!',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[order.user.email],
                    fail_silently=True,
                )
            messages.success(request, f'Order #{order_id} updated successfully.')
        except Order.DoesNotExist:
            messages.error(request, f'Order #{order_id} not found.')

        return redirect('admin-dashboard')  # Avoid form re-submission

    # Order stats
    total_orders = Order.objects.count()
    paid_orders = Order.objects.filter(is_paid=True).count()
    unpaid_orders = Order.objects.filter(is_paid=False).count()
    total_revenue = Order.objects.filter(is_paid=True).aggregate(Sum('total_price'))['total_price__sum'] or 0
    recent_orders = Order.objects.filter(created_at__gte=now() - timedelta(days=7))

    context = {
        'total_orders': total_orders,
        'paid_orders': paid_orders,
        'unpaid_orders': unpaid_orders,
        'total_revenue': total_revenue,
        'recent_orders': recent_orders,
    }
    return render(request, 'admin_dashboard.html', context)

def checkout_success(request, order_id):
    order = Order.objects.get(id=order_id)  # Get the order from DB
    user = order.user  # Get the user from the order

    # Now call the function with correct references
    send_order_confirmation_email(user.email, order)

    return render(request, 'orders/checkout_success.html', {'order': order})