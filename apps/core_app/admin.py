from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import (
    Course, Cohort, 
    PaymentPlan, PaymentLog, SalaryPayment, OfficeExpense, Notification
)

User = get_user_model()


User = get_user_model()


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Course admin"""
    list_display = ['title', 'duration_weeks', 'created_by', 'created_at']
    list_filter = ['created_at', 'duration_weeks']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(Cohort)
class CohortAdmin(admin.ModelAdmin):
    """Cohort admin"""
    list_display = ['name', 'course', 'instructor', 'start_date', 'end_date', 'student_count']
    list_filter = ['course', 'start_date', 'end_date']
    search_fields = ['name', 'course__title', 'instructor__email']
    filter_horizontal = ['students']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-start_date']
    
    def student_count(self, obj):
        return obj.students.count()
    student_count.short_description = 'Students'


@admin.register(PaymentPlan)
class PaymentPlanAdmin(admin.ModelAdmin):
    """Payment Plan admin"""
    list_display = [
        'student', 'course', 'plan_type', 'amount_total', 
        'amount_paid', 'amount_remaining', 'status', 'created_at'
    ]
    list_filter = ['plan_type', 'status', 'created_at']
    search_fields = ['student__email', 'student__first_name', 'student__last_name', 'course__title']
    readonly_fields = ['created_at', 'updated_at', 'amount_remaining', 'payment_percentage']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Student & Course', {
            'fields': ('student', 'course', 'cohort')
        }),
        ('Payment Details', {
            'fields': ('plan_type', 'amount_total', 'amount_paid', 'status')
        }),
        ('Computed Fields', {
            'fields': ('amount_remaining', 'payment_percentage'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PaymentLog)
class PaymentLogAdmin(admin.ModelAdmin):
    """Payment Log admin"""
    list_display = [
        'student', 'amount', 'payment_method', 
        'payment_date', 'recorded_by'
    ]
    list_filter = ['payment_method', 'payment_date']
    search_fields = ['student__email', 'student__first_name', 'student__last_name']
    readonly_fields = ['created_at', 'payment_date']
    ordering = ['-payment_date']
    
    fieldsets = (
        ('Payment Info', {
            'fields': ('payment_plan', 'student', 'amount', 'payment_method')
        }),
        ('Receipt & Notes', {
            'fields': ('receipt_url', 'notes')
        }),
        ('Admin', {
            'fields': ('recorded_by', 'payment_date', 'created_at')
        }),
    )


@admin.register(SalaryPayment)
class SalaryPaymentAdmin(admin.ModelAdmin):
    """Salary Payment admin"""
    list_display = [
        'staff', 'amount_due', 'amount_paid', 
        'amount_remaining', 'status', 'payment_date'
    ]
    list_filter = ['status', 'payment_date']
    search_fields = ['staff__email', 'staff__first_name', 'staff__last_name']
    readonly_fields = ['created_at', 'updated_at', 'amount_remaining']
    ordering = ['-payment_date']
    
    fieldsets = (
        ('Staff & Payment', {
            'fields': ('staff', 'amount_due', 'amount_paid', 'status')
        }),
        ('Payment Details', {
            'fields': ('paid_by', 'payment_date', 'notes')
        }),
        ('Computed', {
            'fields': ('amount_remaining',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(OfficeExpense)
class OfficeExpenseAdmin(admin.ModelAdmin):
    """Office Expense admin"""
    list_display = [
        'title', 'category', 'amount', 'status', 
        'expense_date', 'submitted_by', 'approved_by'
    ]
    list_filter = ['status', 'category', 'expense_date', 'created_at']
    search_fields = ['title', 'description', 'submitted_by__email']
    readonly_fields = ['created_at', 'updated_at', 'approved_at', 'paid_at']
    ordering = ['-expense_date', '-created_at']
    
    fieldsets = (
        ('Expense Details', {
            'fields': ('title', 'description', 'category', 'amount', 'expense_date')
        }),
        ('Status & Payment', {
            'fields': ('status', 'payment_method', 'receipt_url')
        }),
        ('Tracking', {
            'fields': ('submitted_by', 'approved_by', 'paid_by')
        }),
        ('Notes', {
            'fields': ('notes', 'rejection_reason'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'approved_at', 'paid_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_expenses', 'reject_expenses', 'mark_as_paid']
    
    def approve_expenses(self, request, queryset):
        count = 0
        for expense in queryset.filter(status='pending'):
            expense.approve(request.user)
            count += 1
        self.message_user(request, f"{count} expense(s) approved.")
    approve_expenses.short_description = "Approve selected expenses"
    
    def reject_expenses(self, request, queryset):
        count = 0
        for expense in queryset.filter(status='pending'):
            expense.reject(request.user, "Rejected via bulk action")
            count += 1
        self.message_user(request, f"{count} expense(s) rejected.")
    reject_expenses.short_description = "Reject selected expenses"
    
    def mark_as_paid(self, request, queryset):
        count = 0
        for expense in queryset.filter(status='approved'):
            expense.mark_as_paid(request.user, 'transfer')
            count += 1
        self.message_user(request, f"{count} expense(s) marked as paid.")
    mark_as_paid.short_description = "Mark selected as paid"


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Notification admin"""
    list_display = ['recipient', 'type', 'message_preview', 'is_read', 'created_at']
    list_filter = ['type', 'is_read', 'created_at']
    search_fields = ['recipient__email', 'message']
    readonly_fields = ['created_at', 'read_at']
    ordering = ['-created_at']
    
    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message'
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        for notification in queryset:
            notification.mark_as_read()
        self.message_user(request, f"{queryset.count()} notification(s) marked as read.")
    mark_as_read.short_description = "Mark selected as read"
    
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False, read_at=None)
        self.message_user(request, f"{queryset.count()} notification(s) marked as unread.")
    mark_as_unread.short_description = "Mark selected as unread"