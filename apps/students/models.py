import uuid
from django.db import models
from django.conf import settings
from apps.base.models import BaseModel
from apps.batch.models import Batch
from datetime import timedelta
from django.utils import timezone


GENDER_CHOICES = [
    ("MALE", "Male"),
    ("FEMALE", "Female"),
]

STATUS_CHOICES = [
    ("PENDING", "Pending"),
    ("ACTIVE", "Active"),
    ("COMPLETED", "Completed"),
    ("DROPPED", "Dropped"),
    ("SUSPENDED", "Suspended"),
]


class StudentProfile(BaseModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_profile"
    )
    
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    profile_picture = models.ImageField(upload_to="student_profiles/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["user__first_name"]

    def __str__(self):
        return f"{self.student_id} - {self.user.get_full_name()}"


class Course(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(default="", null=True, blank=True)
    description = models.TextField()

    def __str__(self):
        return self.name


class StudentEnrollment(BaseModel):
    """
    Unified model:
    - Student can enroll in multiple courses.
    - Batch is optional at first.
    - Admin can assign batch later.
    """
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="enrollments"
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="enrollments"
    )
    batch = models.ForeignKey(
        Batch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="enrollments"
    )
    enrollment_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    total_fee = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_fee = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    completion_date = models.DateField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)

    class Meta:
        ordering = ["-enrollment_date"]
        constraints = [
            models.UniqueConstraint(fields=["student", "course"], name="unique_student_course_enrollment")
        ]

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.course.name} ({self.status})"
    def save(self, *args, **kwargs):
            # Auto-calculate final fee
        self.final_fee = self.total_fee - self.discount_amount

            # Automatically set completion_date 6 months later if not set
        if not self.completion_date:
            self.completion_date = timezone.now() + timedelta(days=180)

        # Auto-mark as completed if current date >= completion_date
        if self.completion_date and timezone.now() >= self.completion_date:
            self.is_completed = True
            self.status = "COMPLETED"

        super().save(*args, **kwargs)

        #when a student enrolls —  what the code does
# → It automatically sets their completion date = 6 months from today.

# If the current date reaches or passes that date —
# → Their enrollment is automatically marked completed