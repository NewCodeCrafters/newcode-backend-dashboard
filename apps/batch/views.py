from django.shortcuts import render
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView, get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from .models import Batch
from .serializers import BatchSerializers

# List all batches or create a new one
class BatchListCreateView(GenericAPIView):
    queryset = Batch.objects.all()
    serializer_class = BatchSerializers
    permission_classes = [permissions.IsAdminUser]  # Only admins can add/view batches

    @swagger_auto_schema(operation_summary="Get all batches")
    def get(self, request):
        batches = self.get_queryset()
        serializer = self.get_serializer(batches, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_summary="Create a new batch")
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Get, update, or delete a specific batch
class BatchDetailView(GenericAPIView):
    queryset = Batch.objects.all()
    serializer_class = BatchSerializers
    permission_classes = [permissions.IsAdminUser]

    def get_object(self, pk):
        return get_object_or_404(Batch, pk=pk)

    @swagger_auto_schema(operation_summary="Get a single batch by ID")
    def get(self, request, pk):
        batch = self.get_object(pk)
        serializer = self.get_serializer(batch)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_summary="Update a batch")
    def put(self, request, pk):
        batch = self.get_object(pk)
        serializer = self.get_serializer(batch, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_summary="Delete a batch")
    def delete(self, request, pk):
        batch = self.get_object(pk)
        batch.delete()
        return Response({"message": "Batch deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
