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
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
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
