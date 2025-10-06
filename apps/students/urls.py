from django.urls import path
from .views import StudentProfileView, AdminStudentProfileView, StudentBatchEnrollmentView

urlpatterns = [
    path("student/profile/", StudentProfileView.as_view(), name="student-profile"),
    path("admin/profiles/", AdminStudentProfileView.as_view(), name="admin-profile-list"),
    path('student/enrollment/', StudentBatchEnrollmentView.as_view(), name='student-batch-enrollment')
]
