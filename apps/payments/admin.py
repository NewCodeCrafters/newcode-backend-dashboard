from django.contrib import admin
from .models import PaymentPlan, PaymentTransaction

@admin.register(PaymentPlan)
class PaymentPlanAdmin(admin.ModelAdmin):
    list_display = ("plan_name", "enrollment", "total_amount", "number_of_installments", "created_by", "created_at")
    list_filter = ("created_at", "created_by")
    search_fields = ("plan_name", "enrollment__student__first_name", "enrollment__student__last_name")
    ordering = ("-created_at",)

from django.contrib import admin
from .models import PaymentTransaction


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'amount',
        'payment_method',
        'payment_status',
        'payment_date',
        'created_at',
    )
    list_filter = (
        'payment_method',
        'payment_status',
        'payment_date',
        'created_at',
    )
    search_fields = (
        'student__first_name',
        'student__last_name',
        'enrollment__batch__batch_name',
    )
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    date_hierarchy = 'payment_date'
    list_per_page = 25
