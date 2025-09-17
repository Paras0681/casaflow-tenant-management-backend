from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.tenants.models import TenantsFiles
from apps.notifications.utils.send_notification import send_notification

@receiver(post_save, sender=TenantsFiles)
def notify_tenants_invoice_upload(sender, instance, created, **kwargs):
    if created and instance.file_type == "invoice_bill":
        account = instance.account
        subject = "Your Monthly Invoice is Ready"
        text_message = (
        f"Hello {account.first_name},\n\n"
        "Your monthly invoice has just been generated. "
        "Please log in to the application and complete the payment.\n\n"
        "Thank you,\nTenant Management Team"
        )
        html_message = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <h3 style="color: #2c3e50;">Hello {account.first_name},</h2>
            <p>Your monthly <strong>invoice</strong> has just been generated.</p>
            <p>Please log in to the application and complete the payment.</p>
            <p style="margin:20px 0;">
                <a href="https://picsum.photos/id/237/200/300" 
                   style="background-color:#4CAF50; color:white; padding:10px 15px; text-decoration:none; border-radius:5px;">
                   Login
                </a>
            </p>
            <p>Thank you,<br>Tenant Management Team</p>
        </body>
        </html>
        """
        send_notification(
            user=account,
            title=subject,
            message=text_message,
            html_message=html_message,
            notification_type="invoice"
        )

@receiver(post_save, sender=TenantsFiles)
def notify_admin_file_upload(sender, instance, created, **kwargs):
    if created and instance.file_type == "payment_receipt":
        account = instance.account
        payment = account.payments.reverse().first()
        subject = f"Payment screenshot uploaded by {payment.uploaded_by} just now."
        text_message = (
        f"Hello Staff,\n\n"
        f"Payment of {payment.amount}/- having UTR:{payment.payment_utr} for invoice number {payment.invoice_id} have been made.\n\n"
        "Thank you,\nTenant Management Team"
        )
        html_message = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <h3 style="color: #2c3e50;">Hello Staff,</h3>
            <p>Payment of {payment.amount}/- having UTR:{payment.payment_utr} for invoice number {payment.invoice_id} have been made.</p>
            <p>Please verify.</p>
            <p style="margin:20px 0;">
                <a href="https://picsum.photos/id/237/200/300" 
                   style="background-color:#4CAF50; color:white; padding:10px 15px; text-decoration:none; border-radius:5px;">
                   Login
                </a>
            </p>
            <p>Thank you,<br>Tenant Management Team</p>
        </body>
        </html>
        """
        send_notification(
            user=account,
            title=subject,
            message=text_message,
            html_message=html_message,
            notification_type="payment"
        )
    else:
        account = instance.account
        subject = f"{instance.file_type.replace("_", " ").upper()} has been uploaded by {account.first_name}."
        text_message = (
        f"Hello Staff,\n\n"
        f"{instance.file_type} has been uploaded by {account.first_name} here's the quick link {instance.file_url}.\n\n"
        "Thank you,\nTenant Management Team"
        )
        html_message = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <h3 style="color: #2c3e50;">Hello Staff,</h3>
            <p>Please check the {instance.file_type.replace("_", " ").upper()} uploaded by {account.first_name}.</p>
            <p>Here's the quick link {instance.file_url}.</p>
            <p style="margin:20px 0;">
                <a href="{instance.download_url}" 
                   style="background-color:#4CAF50; color:white; padding:10px 15px; text-decoration:none; border-radius:5px;">
                   Download
                </a>
            </p>
            <p>Thank you,<br>Tenant Management Team</p>
        </body>
        </html>
        """
        send_notification(
            user=account,
            title=subject,
            message=text_message,
            html_message=html_message,
            notification_type="file"
        )