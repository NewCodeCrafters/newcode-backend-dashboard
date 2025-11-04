from django.contrib import admin
from .models import Course, StudentProfile, StudentEnrollment


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "description")


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "phone_number",
        "gender",
        "city",
        "state",
        "created_at",
    )
    search_fields = (
        "user__first_name",
        "user__last_name",
        "user__email",
        "phone_number",
        "city",
        "state",
    )
    list_filter = ("gender", "state", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("user__first_name",)


@admin.register(StudentEnrollment)
class StudentEnrollmentAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "course",
        "status",
        "total_fee",
        "discount_amount",
        "final_fee",
        "enrollment_date",
        "completion_date",
        "is_completed",
    )
    list_filter = ("status", "is_completed", "enrollment_date", "completion_date")
    search_fields = (
        "student__first_name",
        "student__last_name",
        "course__name",
    )
    readonly_fields = ("final_fee", "completion_date", "is_completed")
    ordering = ("-enrollment_date",)

    def save_model(self, request, obj, form, change):
        """
        Automatically calculates final_fee and completion_date.
        """
        obj.save()
