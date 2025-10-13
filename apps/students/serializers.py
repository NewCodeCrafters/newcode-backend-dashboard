from rest_framework import serializers
from .models import Course, StudentProfile, StudentBatchEnrollment


class CourseSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(read_only=True)

    class Meta:
        model = Course
        fields = "__all__"
        read_only_fields = ("slug", "created_at", "updated_at")


class StudentProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = StudentProfile
        fields = "__all__"
        read_only_fields = ("student_id", "created_at", "updated_at", "user")


class StudentBatchEnrollmentSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField(read_only=True)
    final_fee = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = StudentBatchEnrollment
        fields = "__all__"
        read_only_fields = ("final_fee", "enrollment_date", "student")
