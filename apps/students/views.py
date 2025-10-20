<<<<<<< HEAD
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from .models import StudentProfile, StudentEnrollment, Course
from .serializers import (
    StudentEnrollmentProgressSerializer,
    StudentProfileSerializer,
    StudentProfileWithEnrollmentsSerializer,
    StudentEnrollmentSerializer,
    CourseSerializer,
)
from apps.batch.models import Batch
from django.contrib.auth import get_user_model

User = get_user_model()


#studentprofile

class StudentProfileView(generics.RetrieveUpdateDestroyAPIView):
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return StudentProfile.objects.get(user=self.request.user)

    @swagger_auto_schema(
        operation_summary="Get your student profile",
        operation_description="Retrieve the logged-in student's profile with all course enrollments.",
        responses={200: StudentProfileWithEnrollmentsSerializer()},
    )
    def get(self, request):
        profile = self.get_object()
        serializer = StudentProfileWithEnrollmentsSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Create your student profile",
        operation_description="Authenticated users can create their student profile.",
        request_body=StudentProfileSerializer,
        responses={201: StudentProfileSerializer()},
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


#course enrollment with no batch yet

class StudentCourseEnrollmentView(generics.GenericAPIView):
    serializer_class = StudentEnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return StudentEnrollment.objects.filter(student=self.request.user)

    @swagger_auto_schema(
        operation_summary="List your course enrollments",
        operation_description="Displays all courses the logged-in student has enrolled in.",
        responses={200: StudentEnrollmentSerializer(many=True)},
    )
    def get(self, request):
        enrollments = self.get_queryset()
        serializer = self.get_serializer(enrollments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Enroll in a course",
        operation_description="Allows a student to enroll in one or more courses (batch not required yet).",
        request_body=StudentEnrollmentSerializer,
        responses={201: StudentEnrollmentSerializer()},
=======
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from .models import Course, StudentProfile, StudentBatchEnrollment
from .serializers import (
    CourseSerializer,
    StudentProfileSerializer,
    StudentBatchEnrollmentSerializer,
)

# ==============================================
# ✅ COURSES ENDPOINTS
# ==============================================
class CourseListCreateView(generics.ListCreateAPIView):
    queryset = Course.objects.all().order_by("name")
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAdminUser]

    @swagger_auto_schema(
        operation_summary="GET /students/courses/ – List all courses",
        tags=["Courses"],
        description="""
Retrieve a complete list of all available courses.

Only **admins** can access this endpoint.

It returns course details such as:
- Name
- Description
- Duration
- Price
        """,
        responses={200: CourseSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="POST /students/courses/ – Create a new course",
        tags=["Courses"],
        description="""
Allows an **admin** to create a new course by providing:

- Course name  
- Description  
- Duration  
- Price  

This registers the new course into the system.
        """,
        request_body=CourseSerializer,
        responses={201: CourseSerializer()},
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = "pk"

    @swagger_auto_schema(
        operation_summary="GET /students/courses/{id}/ – Retrieve a course by ID",
        tags=["Courses"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="PUT /students/courses/{id}/ – Update a course by ID",
        tags=["Courses"],
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="PATCH /students/courses/{id}/ – Partially update a course by ID",
        tags=["Courses"],
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="DELETE /students/courses/{id}/ – Delete a course by ID",
        tags=["Courses"],
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


# ==============================================
# ✅ STUDENT PROFILES ENDPOINTS
# ==============================================
class StudentProfileListCreateView(generics.ListCreateAPIView):
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer
    permission_classes = [permissions.IsAdminUser]

    @swagger_auto_schema(
        operation_summary="GET /students/profiles/ – List all student profiles",
        tags=["Profiles"],
        description="""
Displays all student profiles in the system.

Only **admins** can access this endpoint.
        """,
        responses={200: StudentProfileSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="POST /students/profiles/ – Create a new student profile",
        tags=["Profiles"],
        description="""
Allows **admins** to manually create a student profile.

Useful when a user has registered but no student profile exists yet.
        """,
        request_body=StudentProfileSerializer,
        responses={201: StudentProfileSerializer()},
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudentProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = "pk"

    @swagger_auto_schema(
        operation_summary="GET /students/profiles/{id}/ – Retrieve a student profile by ID",
        tags=["Profiles"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="PUT /students/profiles/{id}/ – Update a student profile by ID",
        tags=["Profiles"],
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="DELETE /students/profiles/{id}/ – Delete a student profile by ID",
        tags=["Profiles"],
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


# ==============================================
# ✅ ENROLLMENTS ENDPOINTS
# ==============================================
class EnrollmentListCreateView(generics.ListCreateAPIView):
    queryset = StudentBatchEnrollment.objects.all()
    serializer_class = StudentBatchEnrollmentSerializer
    permission_classes = [permissions.IsAdminUser]

    @swagger_auto_schema(
        operation_summary="GET /students/enrollments/ – List all enrollments",
        tags=["Enrollments"],
        description="""
Returns all student enrollments across batches and courses.
        """,
        responses={200: StudentBatchEnrollmentSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="POST /students/enrollments/ – Enroll a student into a batch & course",
        tags=["Enrollments"],
        description="""
Allows an **admin** to enroll a student into a batch and course.

Automatically creates a `StudentProfile` if one doesn’t exist.
        """,
        request_body=StudentBatchEnrollmentSerializer,
        responses={201: StudentBatchEnrollmentSerializer()},
>>>>>>> 45cefa61fb59a6731fb023d3bc59d8ecb9293547
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
<<<<<<< HEAD
        serializer.is_valid(raise_exception=True)
        enrollment = serializer.save(student=request.user)

        # Ensure exact timestamp of enrollment
        if not enrollment.enrollment_date:
            enrollment.enrollment_date = timezone.now()
            enrollment.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


#admin assign batch

class AdminAssignBatchView(generics.GenericAPIView):
    serializer_class = StudentEnrollmentSerializer
    permission_classes = [permissions.IsAdminUser]

    @swagger_auto_schema(
        operation_summary="Assign a batch to an enrolled student (Admin only)",
        operation_description=(
            "Admin assigns a batch to a student who already enrolled in a course. "
            "Provide the student, course, and batch IDs."
        ),
        request_body=StudentEnrollmentSerializer,
        responses={200: StudentEnrollmentSerializer()},
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        enrollment = serializer.save()

        # Auto-set date/time if missing
        if not enrollment.enrollment_date:
            enrollment.enrollment_date = timezone.now()
            enrollment.save()

        return Response(serializer.data, status=status.HTTP_200_OK)



class StudentBatchProgressView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        student = request.user.student_profile
        enrollments = StudentEnrollment.objects.filter(student=student).order_by('-enrollment_date')
        serializer = StudentEnrollmentProgressSerializer(enrollments, many=True, context={'request': request})
        return Response({"progress": serializer.data})

#admin see enrollment

class AdminEnrollmentListView(generics.ListAPIView):
    queryset = StudentEnrollment.objects.all()
    serializer_class = StudentEnrollmentSerializer
    permission_classes = [permissions.IsAdminUser]

    @swagger_auto_schema(
        operation_summary="View all enrollments (Admin only)",
        operation_description="Admin can view all student enrollments with batches and courses.",
        responses={200: StudentEnrollmentSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)



from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import StudentProfile
from .serializers import StudentProfileSerializer


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from apps.students.models import StudentProfile
from apps.students.serializers import StudentProfileSerializer


class GetStudentByUUIDView(APIView):
    """
    Retrieve a student's profile using their UUID-based student_id (e.g. STD-5C3DF1)
    """
=======
        if serializer.is_valid():
            enrollment = serializer.save()
            student_user = enrollment.student
            StudentProfile.objects.get_or_create(user=student_user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EnrollmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = StudentBatchEnrollment.objects.all()
    serializer_class = StudentBatchEnrollmentSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = "pk"
>>>>>>> 45cefa61fb59a6731fb023d3bc59d8ecb9293547

    @swagger_auto_schema(
        operation_summary="GET /students/enrollments/{id}/ – Retrieve enrollment by ID",
        tags=["Enrollments"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="PUT /students/enrollments/{id}/ – Update enrollment by ID",
        tags=["Enrollments"],
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="DELETE /students/enrollments/{id}/ – Delete enrollment by ID",
        operation_description="get atudent that enrolled",
        tags=["Enrollments"],
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
