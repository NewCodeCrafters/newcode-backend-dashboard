from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.mail import send_mail
from .models import StudentEnrollment

@receiver(post_save, sender=StudentEnrollment)
def batch_completion_notification(sender, instance, created, **kwargs):
    """
    Notify students when their batch is ending or completed.
    """
    today = timezone.now().date()
    
    # Only notify if the batch is ending in the current month
    if instance.completion_date and not instance.is_completed:
        months_remaining = (instance.completion_date - today).days // 30
        if months_remaining == 0:
            # Mark as completed
            instance.is_completed = True
            instance.status = "COMPLETED"
            instance.save(update_fields=['is_completed', 'status'])

            # Send notification email
            send_mail(
                subject="Batch Completed",
                message=f"Hello {instance.student.user.get_full_name()}, your batch for {instance.course.name} has ended this month.",
                from_email="d38712653@gmail.com",
                recipient_list=[instance.student.user.email],
                fail_silently=True,
            )
        elif months_remaining == 1:
            # Notify batch is ending next month
            send_mail(
                subject="Batch Ending Soon",
                message=f"Hello {instance.student.user.get_full_name()}, your batch for {instance.course.name} is ending next month.",
                from_email="d38712653@gmail.com",
                recipient_list=[instance.student.user.email],
                fail_silently=True,
            )
