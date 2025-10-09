from django.urls import path
from .views import BatchListView, BatchDetailView

urlpatterns = [
    path('batches/', BatchListView.as_view(), name='batch-list-create'),
    path('batches/<int:pk>/', BatchDetailView.as_view(), name='batch-detail'),
]
