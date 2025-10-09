<<<<<<< HEAD
from django.urls import path
from .views import BatchListView, BatchDetailView

urlpatterns = [
    path('batches/', BatchListView.as_view(), name='batch-list-create'),
    path('batches/<int:pk>/', BatchDetailView.as_view(), name='batch-detail'),
]
=======
from django.urls import path
from .views import BatchListCreateView, BatchDetailView

urlpatterns = [
    path('', BatchListCreateView.as_view(), name='batch-list-create'),
    path('<uuid:pk>/', BatchDetailView.as_view(), name='batch-detail'),
]
>>>>>>> 3199560250fba6a3383b770fa9f2a4427c11b809
