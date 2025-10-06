from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from .models import StudentBatchEnrollment, StudentProfile
from .serializers import (
    StudentBatchEnrollmentSerializer,
    StudentProfileSerializer,
    StudentProfileWithEnrollmentsSerializer,
)

#STUDENT PROFILE 
class StudentProfileView(generics.GenericAPIView):
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return StudentProfile.objects.get(user=self.request.user)

    @swagger_auto_schema(
        operation_summary="Retrieve the logged-in student's profile",
        operation_description="Returns the profile details of the authenticated student along with their enrollments.",
        responses={200: StudentProfileWithEnrollmentsSerializer()},
    )
    def get(self, request):
        profile = self.get_object()
        serializer = StudentProfileWithEnrollmentsSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Create a new student profile",
        operation_description="Authenticated users can create their student profile.",
        request_body=StudentProfileSerializer,
        responses={201: StudentProfileSerializer()},
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Update the student's profile",
        operation_description="Allows the student to update their profile fields.",
        request_body=StudentProfileSerializer,
        responses={200: StudentProfileSerializer()},
    )
    def put(self, request):
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Partially update the student's profile",
        operation_description="Allows partial updates to profile fields.",
        request_body=StudentProfileSerializer,
        responses={200: StudentProfileSerializer()},
    )
    def patch(self, request):
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


# ADMIN VIEW 
class AdminStudentProfileView(generics.GenericAPIView):
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileWithEnrollmentsSerializer
    permission_classes = [permissions.IsAdminUser]

    @swagger_auto_schema(
        operation_summary="List all student profiles",
        operation_description="Returns all student profiles with enrollment details.",
        responses={200: StudentProfileWithEnrollmentsSerializer(many=True)},
    )
    def get(self, request):
        profiles = self.get_queryset()
        serializer = self.get_serializer(profiles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Create a student profile ",
        operation_description="Allows admins to create a student profile for a specific user.",
        request_body=StudentProfileSerializer,
        responses={201: StudentProfileSerializer()},
    )
    def post(self, request):
        serializer = StudentProfileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ADMIN DETAIL VIEW — Single student profile by ID
# class AdminStudentProfileDetailView(generics.GenericAPIView):
#     queryset = StudentProfile.objects.all()
#     serializer_class = StudentProfileWithEnrollmentsSerializer
#     permission_classes = [permissions.IsAdminUser]

#     def get_object(self, pk):
#         try:
#             return StudentProfile.objects.get(pk=pk)
#         except StudentProfile.DoesNotExist:
#             return None

#     @swagger_auto_schema(
#         operation_summary="Retrieve a specific student profile (Admin only)",
#         operation_description="View detailed info of a student profile by ID.",
#         responses={200: StudentProfileWithEnrollmentsSerializer()},
#     )
#     def get(self, request, pk):
#         profile = self.get_object(pk)
#         if not profile:
#             return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
#         serializer = self.get_serializer(profile)
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     @swagger_auto_schema(
#         operation_summary="Update a specific student profile (Admin only)",
#         operation_description="Allows full updates to a specific student profile by ID.",
#         request_body=StudentProfileSerializer,
#         responses={200: StudentProfileSerializer()},
#     )
#     def put(self, request, pk):
#         profile = self.get_object(pk)
#         if not profile:
#             return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
#         serializer = StudentProfileSerializer(profile, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     @swagger_auto_schema(
#         operation_summary="Partially update a student profile (Admin only)",
#         operation_description="Allows partial updates to a specific student profile.",
#         request_body=StudentProfileSerializer,
#         responses={200: StudentProfileSerializer()},
#     )
#     def patch(self, request, pk):
#         profile = self.get_object(pk)
#         if not profile:
#             return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
#         serializer = StudentProfileSerializer(profile, data=request.data, partial=True)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     @swagger_auto_schema(
#         operation_summary="Delete a student profile (Admin only)",
#         operation_description="Allows admins to permanently delete a student profile by ID.",
#         responses={204: "Profile deleted successfully"},
#     )
#     def delete(self, request, pk):
#         profile = self.get_object(pk)
#         if not profile:
#             return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
#         profile.delete()
#         return Response({"message": "Profile deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
