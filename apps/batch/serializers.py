from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Batch

User = get_user_model()

class BatchSerializers(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)
    created_by_id = serializers.PrimaryKeyRelatedField(read_only=True)
    slug = serializers.SlugField(read_only=True)

    class Meta:
        model = Batch
        fields = [
            'id',
            'batch_name',
            'description',
            'start_date',
            'end_date',
            'slug',
            'created_by',
            'created_by_id',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by', 'slug', 'created_by_id']
