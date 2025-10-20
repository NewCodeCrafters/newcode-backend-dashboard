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
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
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

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "student_id",
                openapi.IN_PATH,
                description="UUID-based student ID (e.g., STD-5C3DF1)",
                type=openapi.TYPE_STRING,
                required=True,
            )
        ],
        responses={
            200: openapi.Response("Student profile retrieved successfully", StudentProfileSerializer),
            404: "Student not found",
        },
    )
    def get(self, request, student_id):
        try:
            student = StudentProfile.objects.get(student_id=student_id)
            serializer = StudentProfileSerializer(student)
            return Response(
                {"message": "Student profile retrieved successfully", "data": serializer.data},
                status=status.HTTP_200_OK
            )
        except StudentProfile.DoesNotExist:
            return Response(
                {"error": f"Student with ID '{student_id}' not found"},
                status=status.HTTP_404_NOT_FOUND
            )
