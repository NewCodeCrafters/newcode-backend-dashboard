from django.contrib import admin
from .models import Installment

@admin.register(Installment)
class InstallmentAdmin(admin.ModelAdmin):
    list_display = ("payment_plan", "installment_number", "amount", "due_date", "status")
    list_filter = ("status", "due_date")
    search_fields = ("payment_plan__plan_name", "payment_plan__enrollment__student__first_name", "payment_plan__enrollment__student__last_name")
    ordering = ("payment_plan", "installment_number")
