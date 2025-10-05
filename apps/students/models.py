import uuid
from django.db import models
from django.conf import settings
from apps.base.models import BaseModel
from apps.batch.models import Batch


GENDER_CHOICES = [
    ("MALE", "Male"),
    ("FEMALE", "Female"),
]

STATUS_CHOICES = [
    ("ACTIVE", "Active"),
    ("COMPLETED", "Completed"),
    ("DROPPED", "Dropped"),
    ("SUSPENDED", "Suspended"),
]

COURSE_CHOICES = [
    ("Backend Development", "Backend Development"),
    ("Frontend Development", "Frontend Development"),
    ("Machine Learning", "Machine Learning"),
    ("Data Analysis", "Data Analysis"),
    ("Cyber Security", "Cyber Security"),
]


class StudentProfile(BaseModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_profile"
    )
    student_id = models.CharField(max_length=12, unique=True, editable=False)
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

    def save(self, *args, **kwargs):
        if not self.student_id:
            self.student_id = f"STD-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)


class StudentBatchEnrollment(BaseModel):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="enrollments"
    )
    batch = models.ForeignKey(
        Batch,
        on_delete=models.CASCADE,
        related_name="enrollments"
    )
    enrollment_date = models.DateField(auto_now_add=True)
    course = models.CharField(max_length=100, choices=COURSE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="ACTIVE")
    total_fee = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_fee = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    class Meta:
        pass

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.batch.batch_name} ({self.status})"

    def save(self, *args, **kwargs):
        self.final_fee = self.total_fee - self.discount_amount
        super().save(*args, **kwargs)
