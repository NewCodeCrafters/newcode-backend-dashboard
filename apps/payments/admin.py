from django.contrib import admin
from .models import PaymentPlan, Installment

@admin.register(PaymentPlan)
class PaymentPlanAdmin(admin.ModelAdmin):
    list_display = ("student", "total_amount", "number_of_installments", "is_active")
    list_filter = ("is_active",)
    search_fields = ("student__first_name", "student__last_name", "student__email")

@admin.register(Installment)
class InstallmentAdmin(admin.ModelAdmin):
    list_display = ("payment_plan", "installment_number", "amount", "due_date", "status")
    list_filter = ("status", "due_date")
    search_fields = ("payment_plan__student__first_name", "payment_plan__student__last_name")
