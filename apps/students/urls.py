from django.urls import path
from .views import (
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

    # Student Profiles
    path("profiles/", StudentProfileListCreateView.as_view(), name="student-profile-list-create"),
    path("profiles/<int:pk>/", StudentProfileDetailView.as_view(), name="student-profile-detail"),

    # Enrollments
    path("enrollments/", EnrollmentListCreateView.as_view(), name="enrollment-list-create"),
    path("enrollments/<int:pk>/", EnrollmentDetailView.as_view(), name="enrollment-detail"),
]
