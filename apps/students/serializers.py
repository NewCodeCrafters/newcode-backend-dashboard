from rest_framework import serializers
<<<<<<< HEAD
from django.contrib.auth import get_user_model
from .models import StudentProfile, StudentEnrollment, Course
from apps.batch.models import Batch
from django.utils import timezone
from dateutil.relativedelta import relativedelta
=======
from .models import Course, StudentProfile, StudentBatchEnrollment
>>>>>>> 45cefa61fb59a6731fb023d3bc59d8ecb9293547


class CourseSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(read_only=True)

    class Meta:
        model = Course
        fields = "__all__"
        read_only_fields = ("slug", "created_at", "updated_at")


# STUDENT PROFILE

class StudentProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = StudentProfile
<<<<<<< HEAD
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
        depth = 1
=======
        fields = "__all__"
        read_only_fields = ("student_id", "created_at", "updated_at", "user")
>>>>>>> 45cefa61fb59a6731fb023d3bc59d8ecb9293547



# COURSE

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["id", "name", "slug", "description"]



# STUDENT ENROLLMENT (Unified)

class StudentEnrollmentSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField(read_only=True)
<<<<<<< HEAD
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="student",
        write_only=True
    )

    course = CourseSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(),
        source="course",
        write_only=True
    )

    batch = serializers.StringRelatedField(read_only=True)
    batch_id = serializers.PrimaryKeyRelatedField(
        queryset=Batch.objects.all(),
        source="batch",
        required=False,
        allow_null=True,
        write_only=True
    )

    class Meta:
        model = StudentEnrollment
        fields = [
            "id",
            "student", "student_id",
            "course", "course_id",
            "batch", "batch_id",
            "enrollment_date",
            "status",
            "total_fee",
            "discount_amount",
            "final_fee",
        ]
        read_only_fields = ["final_fee", "enrollment_date"]


class StudentEnrollmentProgressSerializer(StudentEnrollmentSerializer):
    days_remaining = serializers.SerializerMethodField()
    months_remaining = serializers.SerializerMethodField()
    progress_message = serializers.SerializerMethodField()

    class Meta(StudentEnrollmentSerializer.Meta):
        fields = StudentEnrollmentSerializer.Meta.fields + [
            "days_remaining",
            "months_remaining",
            "progress_message",
            "is_completed",
        ]

    def get_days_remaining(self, obj):
        if obj.completion_date:
            today = timezone.localdate()
            remaining_days = (obj.completion_date - today).days
            return max(remaining_days, 0)
        return None

    def get_months_remaining(self, obj):
        if obj.completion_date:
            today = timezone.localdate()
            delta = relativedelta(obj.completion_date, today)
            months = delta.years * 12 + delta.months
            return max(months, 0)
        return None

    def get_progress_message(self, obj):
        if obj.is_completed:
            return "This course/batch has been completed."
        days = self.get_days_remaining(obj)
        if days == 0:
            return "Your batch is ending this week!"
        elif days <= 30:
            return "You have less than a month left."
        else:
            return f"{self.get_months_remaining(obj)} months remaining until completion."

# PROFILE WITH ENROLLMENTS

class StudentProfileWithEnrollmentsSerializer(StudentProfileSerializer):
    enrollments = StudentEnrollmentSerializer(
        many=True,
        read_only=True,
        source="user.enrollments"
    )

    class Meta(StudentProfileSerializer.Meta):
        fields = StudentProfileSerializer.Meta.fields + ["enrollments"]
=======
    final_fee = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = StudentBatchEnrollment
        fields = "__all__"
        read_only_fields = ("final_fee", "enrollment_date", "student")
>>>>>>> 45cefa61fb59a6731fb023d3bc59d8ecb9293547
