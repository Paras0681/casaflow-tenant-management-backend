# notifications/utils/send_notification.py
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from apps.notifications.models import Notification

def send_notification(user, title, message, html_message=None, notification_type=None):
    """
    Sends a notification to the user and stores it in the database.
    Supports both plain text and HTML email versions.
    """
    Notification.objects.create(
        account=user,
        title=title,
        message=message,
        notification_type=notification_type
    )
    email = EmailMultiAlternatives(
        subject=title,
        body=message,  # plain text fallback
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.user.email],
    )
    if html_message:
        email.attach_alternative(html_message, "text/html")

    email.send(fail_silently=True)
