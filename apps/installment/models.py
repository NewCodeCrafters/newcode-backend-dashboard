from django.db import models

from django.db import models
from apps.base.models import BaseModel
from apps.payments.models import PaymentPlan  # assuming this is in the same app or adjust import if needed

INSTALLMENT_STATUS = [
    ("PENDING", "Pending"),
    ("PAID", "Paid"),
    ("OVERDUE", "Overdue"),
    ("WAIVED", "Waived"),
]

class Installment(BaseModel):
    payment_plan = models.ForeignKey(
        PaymentPlan,
        on_delete=models.CASCADE,
        related_name="installments"
    )
    installment_number = models.PositiveIntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=INSTALLMENT_STATUS, default="PENDING")

    class Meta:
        unique_together = ("payment_plan", "installment_number")
        ordering = ["installment_number"]
        verbose_name = "Installment"
        verbose_name_plural = "Installments"

    def __str__(self):
        return f"Installment {self.installment_number} - {self.payment_plan.plan_name} ({self.status})"

