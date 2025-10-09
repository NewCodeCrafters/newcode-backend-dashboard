from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.users.models import User
from apps.payments.models import PaymentTransaction
from apps.batch.models import Batch
from .models import Notification



@receiver(post_save, sender=User)
def create_signup_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            recipient=instance,
            notification_type="NEW_SIGNUP",
            title="Welcome to the Academy!",
            message=f"Hello {instance.get_full_name()}, your account has been successfully created.",
            related_user=instance,
        )



@receiver(post_save, sender=PaymentTransaction)
def payment_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            recipient=instance.user,
            notification_type="PAYMENT_RECEIVED",
            title="Payment Received",
            message=f"Your payment of ₦{instance.amount} has been received successfully.",
            related_payment=instance,
        )


# ✅ When a new batch is created
@receiver(post_save, sender=Batch)
def batch_created_notification(sender, instance, created, **kwargs):
    if created:
        # Example: notify all admins
        admins = User.objects.filter(is_staff=True)
        for admin in admins:
            Notification.objects.create(
                recipient=admin,
                notification_type="BATCH_CREATED",
                title="New Batch Created",
                message=f"A new batch '{instance.batch_name}' has been created.",
                related_batch=instance,
            )
