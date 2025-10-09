from django.urls import path
from .views import StudentProfileView, AdminStudentProfileView, GetStudentByUUIDView

urlpatterns = [
    path("student/profile/", StudentProfileView.as_view(), name="student-profile"),
    path("admin/profiles/", AdminStudentProfileView.as_view(), name="admin-profile-list"),
     path("student/<str:student_id>/", GetStudentByUUIDView.as_view(), name="get_student_by_uuid"),
]
