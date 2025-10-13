from rest_framework import generics, permissions, status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from datetime import date
from .models import Batch
from .serializers import BatchSerializers



class BatchListCreateView(generics.GenericAPIView):
    queryset = Batch.objects.all()
    serializer_class = BatchSerializers
    permission_classes = [permissions.IsAdminUser]

    @swagger_auto_schema(
        operation_summary="List all batches (Admin only)"   ,
        operation_description="Allows admins to view all batches with optional filters for 'status' and 'name'.",
        responses={200: BatchSerializers(many=True)},
    )
    def get(self, request):
        status_filter = request.GET.get('status')
        name = request.GET.get('name')
        today = date.today()
        batches = Batch.objects.all()

        if status_filter == "active":
            batches = batches.filter(start_date__lte=today, end_date__gte=today)
        elif status_filter == "upcoming":
            batches = batches.filter(start_date__gt=today)

        if name:
            batches = batches.filter(batch_name__icontains=name)

        serializer = BatchSerializers(batches, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Create a new batch (Admin only)",
        operation_description="Allows an admin to create a batch. The 'created_by' field is set automatically.",
        request_body=BatchSerializers,
        responses={201: BatchSerializers()},
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)  # ✅ fixed key here
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BatchDetailView(generics.GenericAPIView):
    queryset = Batch.objects.all()
    serializer_class = BatchSerializers
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'

    def get_object(self, pk):
        try:
            return Batch.objects.get(pk=pk)
        except Batch.DoesNotExist:
            return None

    @swagger_auto_schema(
        operation_summary="Retrieve a batch by ID",
        operation_description="Authenticated users can view batch details by ID.",
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
        operation_description="Only the creator (admin who created it) can update this batch.",
        request_body=BatchSerializers,
        responses={200: BatchSerializers()},
    )
    def put(self, request, pk):
        batch = self.get_object(pk)
        if not batch:
            return Response({"detail": "Batch not found."}, status=status.HTTP_404_NOT_FOUND)

        if batch.created_by != request.user:
            return Response({"detail": "You are not allowed to edit this batch."}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(batch, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Partially update a batch by ID",
        operation_description="Allows the creator to partially update batch details.",
        request_body=BatchSerializers,
        responses={200: BatchSerializers()},
    )
    def patch(self, request, pk):
        batch = self.get_object(pk)
        if not batch:
            return Response({"detail": "Batch not found."}, status=status.HTTP_404_NOT_FOUND)

        if batch.created_by != request.user:
            return Response({"detail": "You are not allowed to edit this batch."}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(batch, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Delete a batch by ID",
        operation_description="Allows only the creator to delete a batch.",
        responses={204: "Batch deleted successfully"},
    )
    def delete(self, request, pk):
        batch = self.get_object(pk)
        if not batch:
            return Response({"detail": "Batch not found."}, status=status.HTTP_404_NOT_FOUND)

        if batch.created_by != request.user:
            return Response({"detail": "You are not allowed to delete this batch."}, status=status.HTTP_403_FORBIDDEN)

        batch.delete()
        return Response({"detail": "Batch deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
