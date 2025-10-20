from django.urls import path
from .views import (
    StudentProfileView,
    StudentCourseEnrollmentView,
    StudentBatchProgressView,
    AdminEnrollmentListView,
    AdminAssignBatchView,
    GetStudentByUUIDView,
)

urlpatterns = [
    path("student/profile/", StudentProfileView.as_view(), name="student-profile"),
    path("student/enrollments/", StudentCourseEnrollmentView.as_view(), name="student-enrollments"),
    path("student/batch-progress/", StudentBatchProgressView.as_view(), name="student-batch-progress"),
    path("student/<uuid:student_id>/", GetStudentByUUIDView.as_view(), name="get-student-uuid"),
    path("admin/enrollments/", AdminEnrollmentListView.as_view(), name="admin-enrollment-list"),
    path("admin/assign-batch/", AdminAssignBatchView.as_view(), name="admin-assign-batch"),
]
