from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    recipient_name = serializers.CharField(source="recipient.get_full_name", read_only=True)
    related_user_name = serializers.CharField(source="related_user.get_full_name", read_only=True)

    class Meta:
        model = Notification
        fields = [
            "id",
            "recipient",
            "recipient_name",
            "notification_type",
            "title",
            "message",
            "related_user",
            "related_user_name",
            "related_batch",
            "related_payment",
            "is_read",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
