from django.db import models
from django.conf import settings
from apps.base.models import BaseModel 
from django.utils import timezone


class Batch(BaseModel):
    batch_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    start_date = models.DateField()
    end_date = models.DateField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    max_students = models.PositiveIntegerField(blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,  
        on_delete=models.CASCADE,
        related_name="created_batches"
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_date__gt=models.F("start_date")),
                name="valid_date_range"
            )
        ]
