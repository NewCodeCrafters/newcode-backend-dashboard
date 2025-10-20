from django.urls import path
from .views import (
    PaymentPlanListCreateView,
    PaymentPlanDetailView,
    InstallmentListView,
    InstallmentUpdateView,
)

urlpatterns = [
    path("plans/", PaymentPlanListCreateView.as_view(), name="paymentplan-list-create"),
    path("plans/<int:pk>/", PaymentPlanDetailView.as_view(), name="paymentplan-detail"),
    path("installments/", InstallmentListView.as_view(), name="installment-list"),
    path("installments/<int:pk>/update/", InstallmentUpdateView.as_view(), name="installment-update"),
]
