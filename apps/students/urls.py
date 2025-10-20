from django.urls import path
from .views import (
<<<<<<< HEAD
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
=======
    CourseListCreateView,
    CourseDetailView,
    StudentProfileListCreateView,
    StudentProfileDetailView,
    EnrollmentListCreateView,
    EnrollmentDetailView,
)

urlpatterns = [
    # Courses
    path("courses/", CourseListCreateView.as_view(), name="course-list-create"),
    path("courses/<int:pk>/", CourseDetailView.as_view(), name="course-detail"),
    path("profiles/", StudentProfileListCreateView.as_view(), name="student-profile-list-create"),
    path("profiles/<int:pk>/", StudentProfileDetailView.as_view(), name="student-profile-detail"),
    path("enrollments/", EnrollmentListCreateView.as_view(), name="enrollment-list-create"),
    path("enrollments/<int:pk>/", EnrollmentDetailView.as_view(), name="enrollment-detail"),
>>>>>>> 45cefa61fb59a6731fb023d3bc59d8ecb9293547
]
