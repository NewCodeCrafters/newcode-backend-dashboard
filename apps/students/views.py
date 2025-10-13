from rest_framework import generics, permissions, status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from .models import Course, StudentProfile, StudentBatchEnrollment
from .serializers import (
    CourseSerializer,
    StudentProfileSerializer,
    StudentBatchEnrollmentSerializer,
)


# ========== COURSE VIEWS ==========
class CourseListCreateView(generics.ListCreateAPIView):
    queryset = Course.objects.all().order_by("name")
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAdminUser]

    @swagger_auto_schema(
        operation_summary="List all courses",
        operation_description="Retrieve all available courses.",
        responses={200: CourseSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a new course",
        operation_description="Admin can create a new course.",
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

    @swagger_auto_schema(operation_summary="Retrieve a course by ID")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Update a course by ID")
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Partially update a course by ID")
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Delete a course by ID")
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


# ========== STUDENT PROFILE ==========
class StudentProfileListCreateView(generics.ListCreateAPIView):
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="List all student profiles",
        responses={200: StudentProfileSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a student profile for logged-in user",
        request_body=StudentProfileSerializer,
        responses={201: StudentProfileSerializer()},
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudentProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "pk"

    @swagger_auto_schema(operation_summary="Retrieve a student profile by ID")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


# ========== STUDENT ENROLLMENT ==========
class EnrollmentListCreateView(generics.ListCreateAPIView):
    queryset = StudentBatchEnrollment.objects.all()
    serializer_class = StudentBatchEnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="List all enrollments",
        responses={200: StudentBatchEnrollmentSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        if not request.user.is_staff:
            queryset = self.get_queryset().filter(student=request.user)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Enroll student into a batch & course",
        request_body=StudentBatchEnrollmentSerializer,
        responses={201: StudentBatchEnrollmentSerializer()},
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(student=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EnrollmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = StudentBatchEnrollment.objects.all()
    serializer_class = StudentBatchEnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "pk"

    @swagger_auto_schema(operation_summary="Retrieve enrollment by ID")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
