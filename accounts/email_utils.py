# email_utils.py
from django.core.mail import send_mail
from django.conf import settings

def send_order_confirmation_email(user_email, order_details):
    subject = "Order Confirmation - PyShop"
    message = f"Thank you for your order!\n\nOrder Details:\n{order_details}"
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user_email]

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=False,  # Set to False to raise exceptions on failure
        )
        print(f"Email sent to {user_email}")  # Temporary logging
        return True
    except Exception as e:
        print(f"Failed to send email: {str(e)}")  # Log the error
        return False