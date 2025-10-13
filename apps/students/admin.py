from django.contrib import admin
from .models import Course, StudentProfile, StudentBatchEnrollment


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
    list_display = ("student_id", "user", "gender", "phone_number", "city", "state")
    search_fields = ("student_id", "user__email", "user__first_name", "user__last_name")
    list_filter = ("gender", "state")
    readonly_fields = ("student_id", "created_at", "updated_at")


@admin.register(StudentBatchEnrollment)
class StudentBatchEnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "batch", "course", "status", "final_fee", "enrollment_date")
    search_fields = ("student__email", "batch__batch_name", "course__name")
    list_filter = ("status", "course")
    readonly_fields = ("final_fee", "enrollment_date")
