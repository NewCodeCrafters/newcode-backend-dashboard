from rest_framework import serializers
from django.conf import settings
from .models import StudentProfile, StudentBatchEnrollment
from apps.batch.models import Batch


class StudentProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)  
    user_id = serializers.PrimaryKeyRelatedField(queryset=settings.AUTH_USER_MODEL.objects.all(), source="user", write_only=True)

    class Meta:
        model = StudentProfile
        fields = [
            "id",
            "user", "user_id",
            "student_id",
            "date_of_birth",
            "gender",
            "phone_number",
            "address",
            "city",
            "state",
            "profile_picture",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["student_id", "created_at", "updated_at"]


class StudentBatchEnrollmentSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField(read_only=True)  # shows user full_name
    student_id = serializers.PrimaryKeyRelatedField(queryset=settings.AUTH_USER_MODEL.objects.all(), source="student", write_only=True)

    batch = serializers.StringRelatedField(read_only=True)  # shows batch name
    batch_id = serializers.PrimaryKeyRelatedField(queryset=Batch.objects.all(), source="batch", write_only=True)

    class Meta:
        model = StudentBatchEnrollment
        fields = [
            "id",
            "student", "student_id",
            "batch", "batch_id",
            "enrollment_date",
            "course",
            "status",
            "total_fee",
            "discount_amount",
            "final_fee",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["enrollment_date", "created_at", "updated_at", "final_fee"]

class StudentProfileWithEnrollmentsSerializer(StudentProfileSerializer):
    enrollments = StudentBatchEnrollmentSerializer(many=True, read_only=True, source="user.enrollments")

    class Meta(StudentProfileSerializer.Meta):
        fields = StudentProfileSerializer.Meta.fields + ["enrollments"]
