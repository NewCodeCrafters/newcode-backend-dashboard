from django.urls import path
from .views import BatchListCreateView, BatchDetailView

urlpatterns = [
    path('', BatchListCreateView.as_view(), name='batch-list-create'),
    path('<uuid:pk>/', BatchDetailView.as_view(), name='batch-detail'),
]
