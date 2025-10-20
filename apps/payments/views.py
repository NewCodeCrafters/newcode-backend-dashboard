from rest_framework import generics
from drf_yasg.utils import swagger_auto_schema
from .models import PaymentPlan, Installment
from .serializers import PaymentPlanSerializer, InstallmentSerializer


class PaymentPlanListCreateView(generics.ListCreateAPIView):
    queryset = PaymentPlan.objects.all()
    serializer_class = PaymentPlanSerializer

    @swagger_auto_schema(operation_summary="List or create payment plans")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Create new payment plan for a student")
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class PaymentPlanDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PaymentPlan.objects.all()
    serializer_class = PaymentPlanSerializer

    @swagger_auto_schema(operation_summary="Retrieve, update, or delete a payment plan")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class InstallmentListView(generics.ListAPIView):
    queryset = Installment.objects.all()
    serializer_class = InstallmentSerializer

    @swagger_auto_schema(operation_summary="List all installments")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class InstallmentUpdateView(generics.UpdateAPIView):
    queryset = Installment.objects.all()
    serializer_class = InstallmentSerializer

    @swagger_auto_schema(operation_summary="Mark installment as paid or update status")
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
