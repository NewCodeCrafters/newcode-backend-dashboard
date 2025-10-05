from django.contrib import admin
from .models import StudentBatchEnrollment, StudentProfile
from django import forms

class ProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = '__all__'
        widgets = {
            'dob': forms.DateInput(
                attrs={'type': 'date'},
                format='%Y-%m-%d'
            ),
        }


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("student_id", "user", "date_of_birth", "gender", "phone_number", "city", "state")
    search_fields = ("student_id", "user__username", "user__first_name", "user__last_name", "phone_number", "city", "state")
    list_filter = ("gender", "city", "state", "created_at")
    ordering = ("-created_at",)

@admin.register(StudentBatchEnrollment)
class StudentBatchEnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "batch", "course", "status", "enrollment_date", "total_fee", "discount_amount", "final_fee")
    search_fields = ("student__username", "student__first_name", "student__last_name", "batch__batch_name", "course", "status")
    list_filter = ("course", "status", "enrollment_date")
    ordering = ("-enrollment_date",)



