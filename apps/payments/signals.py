from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import PaymentPlan


@receiver(post_save, sender=PaymentPlan)
def notify_on_payment_plan_creation(sender, instance, created, **kwargs):
    if created:
        student = instance.enrollment.student
        subject = f"New Payment Plan Created for {student.get_full_name()}"
        message = (
            f"Dear {student.get_full_name()},\n\n"
            f"A new payment plan '{instance.plan_name}' has been created for your course enrollment.\n"
            f"Total Amount: ₦{instance.total_amount}\n"
            f"Installments: {instance.number_of_installments}\n\n"
            f"Created By: {instance.created_by.get_full_name()}\n"
            f"Date: {instance.created_at.strftime('%Y-%m-%d')}\n\n"
            f"Best regards,\n"
            f"The Academy Team"
        )

        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [student.email],
                fail_silently=False,
            )
            print(f"✅ Payment plan email sent to {student.email}")
        except Exception as e:
            print(f"❌ Failed to send payment plan email: {e}")
