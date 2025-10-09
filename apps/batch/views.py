from django.shortcuts import render
from .serializers import BatchSerializers
from .models import Batch
from rest_framework.response import Response
from rest_framework import permissions, status, generics
from drf_yasg.utils import swagger_auto_schema
from datetime import date

# create your view here
class BatchListView(generics.GenericAPIView):
    queryset = Batch.objects.all()
    serializer_class = BatchSerializers
    permission_classes = [permissions.IsAdminUser]
    
    @swagger_auto_schema(
        operation_summary= 'this is just for the admins or staff',
        operation_description= 'allows the admins to see all batches',
        request_body= BatchSerializers,
        responses={200: BatchSerializers(many=True)},
    )

    def get(self, request):
        status_filter = request.GET.get('status')
        name = request.GET.get('name')
        today = date.today()
        batchlist = Batch.objects.all()
         
         #to filter batches by status if its active or not 
        if status_filter == "active":
            batchlist = batchlist.filter(start_date__lte=today, end_date__gte=today)
        elif status_filter == "upcoming":
            batchlist = batchlist.filter(start_date__gt=today)

        if name:
            batchlist = batchlist.filter(batch_name__icontains=name)

        serializer = BatchSerializers(batchlist, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_summary='create a new batch using post request',
        operation_description= 'allows the admin to create a new batch',
        request_body= BatchSerializers,
        responses={201: BatchSerializers()}
    )

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    
class  BatchDetailView(generics.GenericAPIView):
    queryset = Batch.objects.all()
    serializer_class = BatchSerializers
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'id'

    @swagger_auto_schema(
        operation_summary= 'allows the admin to view the detail of batches available',
        operation_description= 'only the admin can get a single detail of a particular batch',
        request_body= BatchSerializers,
        responses={200: BatchSerializers()}
    )

    def get(self, request, *args, **kwargs ):
        return self.retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary='update all the fiels of a batch',
        operation_description='allows the admin to update a batch fully',
        request_body=BatchSerializers,
        responses={200: BatchSerializers()}
    )

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary='partially update a batch',
        operation_description='only admin have the access to partially a some fields in the batch',
        request_body= BatchSerializers,
        responses={200: BatchSerializers()}
    )

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary='for the admin to delete a batch fully',
        operation_description= 'allows the admin delete a batch by its id',
        request_body= BatchSerializers,
        responses={204: 'batch deleted sucessfully'}
    )

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


