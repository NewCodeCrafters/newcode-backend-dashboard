from django.db import models
from django.conf import settings
from apps.students.models import StudentBatchEnrollment
from apps.base.models import BaseModel




class PaymentPlan(BaseModel):
    enrollment = models.ForeignKey(StudentBatchEnrollment, on_delete=models.CASCADE, related_name="payment_plans")
    plan_name = models.CharField(max_length=100)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    number_of_installments = models.PositiveIntegerField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_payment_plans")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self): return f"{self.plan_name} ({self.enrollment.student.get_full_name()})"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Payment Plan"
        verbose_name_plural = "Payment Plans"

from django.db import models
from django.utils import timezone
from apps.students.models import StudentProfile as Student
from apps.students.models import StudentBatchEnrollment
from apps.installment.models import Installment  # adjust import if your admin user model is elsewhere


from django.db import models
from django.utils import timezone
from apps.students.models import StudentProfile as Student
from apps.students.models import StudentBatchEnrollment
from apps.installment.models import Installment


class PaymentTransaction(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Cash'),
        ('CARD', 'Card'),
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('UPI', 'UPI'),
        ('CHEQUE', 'Cheque'),
        ('ONLINE', 'Online'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('SUCCESS', 'Success'),
        ('PENDING', 'Pending'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]

    enrollment = models.ForeignKey(
        StudentBatchEnrollment,
        on_delete=models.CASCADE,
        related_name='payment_transactions'
    )
    installment = models.ForeignKey(
        Installment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions'
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='payment_transactions'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES)
    payment_date = models.DateField(default=timezone.now)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='SUCCESS')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Payment Transaction"
        verbose_name_plural = "Payment Transactions"

    