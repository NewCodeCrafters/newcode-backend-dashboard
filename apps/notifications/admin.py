from django.contrib import admin
from .models import Notification
from apps.batch.models import Batch
from apps.payments.models import PaymentTransaction


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "recipient",
        "notification_type",
        "is_read",
        "created_at",
    )
    list_filter = ("notification_type", "is_read", "created_at")
    search_fields = ("title", "message", "recipient__email")
    readonly_fields = ("created_at",)

from django.contrib import admin
from .models import AdminNotification


@admin.register(AdminNotification)
class AdminNotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'admin', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'admin__email')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

