from django.contrib import admin
<<<<<<< HEAD
from .models import StudentEnrollment, StudentProfile
from django import forms
=======
from .models import Course, StudentProfile, StudentBatchEnrollment
>>>>>>> 45cefa61fb59a6731fb023d3bc59d8ecb9293547


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "duration_in_months", "price", "created_at")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "slug", "description")
    list_filter = ("duration_in_months",)
    ordering = ("name",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
<<<<<<< HEAD
    list_display = ("id", "user", "date_of_birth", "gender", "phone_number", "city", "state")
    search_fields = ("student_id", "user__username", "user__first_name", "user__last_name", "phone_number", "city", "state")
    list_filter = ("gender", "city", "state", "created_at")
    ordering = ("-created_at",)  
=======
    list_display = ("student_id", "user", "gender", "phone_number", "city", "state")
    search_fields = ("student_id", "user__email", "user__first_name", "user__last_name")
    list_filter = ("gender", "state")
    readonly_fields = ("student_id", "created_at", "updated_at")

>>>>>>> 45cefa61fb59a6731fb023d3bc59d8ecb9293547

@admin.register(StudentEnrollment)
class StudentBatchEnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "batch", "course", "status", "final_fee", "enrollment_date")
    search_fields = ("student__email", "batch__batch_name", "course__name")
    list_filter = ("status", "course")
    readonly_fields = ("final_fee", "enrollment_date")
