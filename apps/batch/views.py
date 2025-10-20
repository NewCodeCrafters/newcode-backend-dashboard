from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema

from .models import Batch
from .serializers import BatchSerializers


class BatchListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="List all batches",
        operation_description="Retrieve all available batches created by any user.",
        responses={200: BatchSerializers(many=True)},
    )
    def get(self, request):
        batches = Batch.objects.all().order_by('-created_at')
        serializer = BatchSerializers(batches, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Create a new batch",
        operation_description="Create a new batch and assign the authenticated user as the creator.",
        request_body=BatchSerializers,
        responses={201: BatchSerializers()},
    )
    def post(self, request):
        serializer = BatchSerializers(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BatchDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Batch.objects.get(pk=pk)
        except Batch.DoesNotExist:
            return None

    @swagger_auto_schema(
        operation_summary="Retrieve a batch by ID",
        operation_description="Get detailed information about a specific batch using its ID.",
        responses={200: BatchSerializers()},
    )
    def get(self, request, pk):
        batch = self.get_object(pk)
        if not batch:
            return Response({"detail": "Batch not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = BatchSerializers(batch)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Update a batch by ID",
        operation_description="Update batch details (only the creator can update their batch).",
        request_body=BatchSerializers,
        responses={200: BatchSerializers()},
    )
    def put(self, request, pk):
        batch = self.get_object(pk)
        if not batch:
            return Response({"detail": "Batch not found."}, status=status.HTTP_404_NOT_FOUND)

        if batch.created_by != request.user:
            return Response({"detail": "You are not allowed to edit this batch."}, status=status.HTTP_403_FORBIDDEN)

        serializer = BatchSerializers(batch, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Delete a batch by ID",
        operation_description="Delete a batch (only the creator can delete it).",
        responses={204: "No content"},
    )
    def delete(self, request, pk):
        batch = self.get_object(pk)
        if not batch:
            return Response({"detail": "Batch not found."}, status=status.HTTP_404_NOT_FOUND)

        if batch.created_by != request.user:
            return Response({"detail": "You are not allowed to delete this batch."}, status=status.HTTP_403_FORBIDDEN)

        batch.delete()
        return Response({"detail": "Batch deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
