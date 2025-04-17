from django.urls import path
from .import views
from  .views import admin_dashboard, register, user_login, user_logout, activate, home, test_mail, email_verification_sent

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('accounts/login/', user_login, name='user_login'),
    path('logout',user_logout, name='logout'),
    path('activate/<uidb64>/<token>/', activate, name='activate'),
    path('', home, name='home'),
    path('test_mail/', test_mail, name='test_mail'),
    path('email_verification_sent/', email_verification_sent, name='email_verification_sent'),
    path('admin-dashboard/', admin_dashboard, name='admin-dashboard'),
]