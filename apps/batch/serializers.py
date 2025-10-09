from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Batch
<<<<<<< HEAD
from django.conf import settings
from apps.users.models import User

class BatchSerializers(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)
    created_by_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='created_by',write_only=True, required=False)
=======

User = get_user_model()

class BatchSerializers(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)
    created_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='created_by',
        write_only=True,
        required=False
    )
>>>>>>> 3199560250fba6a3383b770fa9f2a4427c11b809

    class Meta:
        model = Batch
        fields = [
            'id',
            'batch_name',
            'description',
            'start_date',
            'end_date',
            'price',
            'created_by',
            'created_by_id',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by']
