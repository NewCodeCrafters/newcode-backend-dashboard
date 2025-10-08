from django.db import models
from django.utils import timezone
from apps.users.models import User
from apps.batch.models import Batch
from apps.payments.models import PaymentTransaction  
NOTIFICATION_TYPE_CHOICES = [
        ('NEW_SIGNUP', 'New Signup'),
        ('PAYMENT_RECEIVED', 'Payment Received'),
        ('PAYMENT_OVERDUE', 'Payment Overdue'),
        ('BATCH_CREATED', 'Batch Created'),
        ('STUDENT_ENROLLED', 'Student Enrolled'),
        ('SYSTEM', 'System'),
    ]

class Notification(models.Model):
    

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(
        max_length=50,
        choices=NOTIFICATION_TYPE_CHOICES
    )
    title = models.CharField(max_length=200)
    message = models.TextField()

    related_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='related_notifications'
    )
    related_batch = models.ForeignKey(
        Batch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications'
    )
    related_payment = models.ForeignKey(
        PaymentTransaction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications'
    )

    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        return f"{self.title} - {self.recipient.get_full_name()}"
