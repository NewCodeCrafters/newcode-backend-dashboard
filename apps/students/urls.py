from django.urls import path
<<<<<<< HEAD
from .views import StudentProfileView, AdminStudentProfileView, StudentBatchEnrollmentView
=======
from .views import StudentProfileView, AdminStudentProfileView, GetStudentByUUIDView
>>>>>>> 3199560250fba6a3383b770fa9f2a4427c11b809

urlpatterns = [
    path("student/profile/", StudentProfileView.as_view(), name="student-profile"),
    path("admin/profiles/", AdminStudentProfileView.as_view(), name="admin-profile-list"),
<<<<<<< HEAD
    path('student/enrollment/', StudentBatchEnrollmentView.as_view(), name='student-batch-enrollment')
=======
     path("student/<str:student_id>/", GetStudentByUUIDView.as_view(), name="get_student_by_uuid"),
>>>>>>> 3199560250fba6a3383b770fa9f2a4427c11b809
]
