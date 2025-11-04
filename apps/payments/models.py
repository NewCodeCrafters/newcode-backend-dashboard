from django.db import models
from django.conf import settings
from apps.students.models import StudentEnrollment
from apps.base.models import BaseModel
from apps.students.models import StudentProfile
from django.conf import settings
from django.utils import timezone

PAYMENT_FREQUENCY = [
    ("MONTHLY", "Monthly"),
    ("TERM", "Per Term"),
    ("CUSTOM", "Custom"),
]

INSTALLMENT_STATUS = [
    ("PENDING", "Pending"),
    ("PAID", "Paid"),
    ("OVERDUE", "Overdue"),
    ("WAIVED", "Waived"),
]


class PaymentPlan(BaseModel):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name="payment_plans"
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    number_of_installments = models.PositiveIntegerField()
    frequency = models.CharField(max_length=20, choices=PAYMENT_FREQUENCY, default="TERM")
    start_date = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.get_full_name}"

    def generate_installments(self):
        from datetime import timedelta

        installment_amount = self.total_amount / self.number_of_installments
        current_date = self.start_date

        for i in range(1, self.number_of_installments + 1):
            Installment.objects.create(
                payment_plan=self,
                installment_number=i,
                amount=installment_amount,
                due_date=current_date,
            )
            current_date += timedelta(days=30)  


class Installment(BaseModel):
    payment_plan = models.ForeignKey(PaymentPlan, on_delete=models.CASCADE, related_name="installments")
    installment_number = models.PositiveIntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=INSTALLMENT_STATUS, default="PENDING")
    payment_reference = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        unique_together = ("payment_plan", "installment_number")
        ordering = ["installment_number"]

    def __str__(self):
        return f"Installment {self.installment_number} - {self.payment_plan.student.full_name}"

    def mark_as_paid(self, reference):
        self.status = "PAID"
        self.payment_reference = reference
        self.save()
