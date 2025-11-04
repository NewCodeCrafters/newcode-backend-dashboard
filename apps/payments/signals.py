from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import PaymentPlan


@receiver(post_save, sender=PaymentPlan)
def notify_on_payment_plan_creation(sender, instance, created, **kwargs):
    if created:
        student = instance.student
        full_name = student.get_full_name()  

        subject = f"New Payment Plan Created for {full_name}"
        message = (
            f"Dear {full_name},\n\n"
            f"A new payment plan has been created for your account.\n"
            f"Total Amount: ₦{instance.total_amount}\n"
            f"Installments: {instance.number_of_installments}\n"
            f"Frequency: {instance.frequency}\n"
            f"Start Date: {instance.start_date.strftime('%Y-%m-%d')}\n\n"
            f"Please log in to your student portal to view the details of your payment schedule.\n\n"
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
