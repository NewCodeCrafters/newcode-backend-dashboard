from django.contrib import admin
from .models import AdminNotification, Notification, EmailQueue
from django.utils import timezone


# --------------------------
# Admin Notification Admin
# --------------------------
@admin.register(AdminNotification)
class AdminNotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'admin', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'admin__email')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)


# --------------------------
# User Notification Admin
# --------------------------
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "recipient", "notification_type", "is_read", "created_at")
    list_filter = ("notification_type", "is_read", "created_at")
    search_fields = ("title", "message", "recipient__email")
    readonly_fields = ("created_at",)


# --------------------------
# Email Queue Admin
# --------------------------
@admin.register(EmailQueue)
class EmailQueueAdmin(admin.ModelAdmin):
    list_display = (
        'recipient_email',
        'subject',
        'email_type',
        'status',
        'attempts',
        'created_at',
        'sent_at',
    )
    list_filter = ('status', 'email_type', 'created_at')
    search_fields = ('recipient_email', 'subject')
    readonly_fields = ('created_at', 'sent_at')

    # Admin actions for bulk update
    actions = ['mark_as_sent', 'retry_failed']

    @admin.action(description="✅ Mark selected emails as sent")
    def mark_as_sent(self, request, queryset):
        queryset.update(status='SENT', sent_at=timezone.now())

    @admin.action(description="🔁 Retry failed emails (reset to pending)")
    def retry_failed(self, request, queryset):
        queryset.filter(status='FAILED').update(status='PENDING', attempts=0)
