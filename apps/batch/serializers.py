from rest_framework import serializers
from .models import Batch
from django.conf import settings

class BatchSerializers(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)
    created_by_id = serializers.PrimaryKeyRelatedField(queryset=settings.AUTH_USER_MODEL.objects.all(), sources='created_by',write_only=True, required=False)

    class Meta:
        model = Batch
        fields = ['id', 'batch_name', 'description', 'start_date', 'end_date', 'price', 'max_student', 'created_by', 'created_by_id', 'created_at', 'updated_at']

        read_only_fields = ['created_at', 'updated_at', 'created_by']