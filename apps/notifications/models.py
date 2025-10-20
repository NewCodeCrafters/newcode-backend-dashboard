from django.db import models
from django.utils import timezone
from apps.users.models import User
from apps.batch.models import Batch
from apps.payments.models import PaymentPlan


NOTIFICATION_TYPE_CHOICES = [
    ("NEW_SIGNUP", "New Signup"),
    ("PAYMENT_RECEIVED", "Payment Received"),
    ("PAYMENT_OVERDUE", "Payment Overdue"),
    ("BATCH_CREATED", "Batch Created"),
    ("STUDENT_ENROLLED", "Student Enrolled"),
    ("SYSTEM", "System"),
]

USER_NOTIFICATION_TYPE_CHOICES = [
    ("PAYMENT_OVERDUE", "Payment Overdue"),
    ("STUDENT_ENROLLED", "Student Enrolled"),
    ("PAYMENT_RECEIVED", "Payment Received"),
]


# ==========================
# ADMIN NOTIFICATIONS MODEL
# ==========================
class AdminNotification(models.Model):
    admin = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={"is_staff": True},
        related_name="admin_notifications",
    )
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    related_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="related_admin_notifications",
    )
    related_batch = models.ForeignKey(
        Batch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="admin_batch_notifications",
    )
    related_payment = models.ForeignKey(
        PaymentPlan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="admin_payment_notifications",
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Admin Notification"
        verbose_name_plural = "Admin Notifications"

    def __str__(self):
        return f"{self.notification_type} - {self.title}"


class Notification(models.Model):
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user_notifications",
    )
    notification_type = models.CharField(max_length=50, choices=USER_NOTIFICATION_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    related_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="related_user_notifications",
    )
    related_batch = models.ForeignKey(
        Batch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="user_batch_notifications",
    )
    related_payment = models.ForeignKey(
        PaymentPlan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="user_payment_notifications",
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        return f"{self.title} → {self.recipient.get_full_name()}"


class EmailQueue(models.Model):
    EMAIL_TYPE_CHOICES = [
        ("VERIFICATION", "Verification"),
        ("NEW_SIGNUP_ALERT", "New Signup Alert"),
        ("PAYMENT_CONFIRMATION", "Payment Confirmation"),
        ("PAYMENT_REMINDER", "Payment Reminder"),
        ("ENROLLMENT_CONFIRMATION", "Enrollment Confirmation"),
        ("GENERAL", "General"),
    ]

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("SENT", "Sent"),
        ("FAILED", "Failed"),
    ]

    recipient_email = models.EmailField(max_length=255)
    recipient_name = models.CharField(max_length=200, blank=True, null=True)
    subject = models.CharField(max_length=500)
    body = models.TextField()
    email_type = models.CharField(max_length=50, choices=EMAIL_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    attempts = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Email Queue"
        verbose_name_plural = "Email Queue"

    def __str__(self):
        return f"{self.subject} → {self.recipient_email} ({self.status})"
