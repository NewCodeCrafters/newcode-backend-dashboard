from django.urls import path
from .views import NotificationListView, MarkNotificationReadView, UnreadNotificationCountView

urlpatterns = [
    path("", NotificationListView.as_view(), name="notification_list"),
    path("<int:id>/read/", MarkNotificationReadView.as_view(), name="mark_notification_read"),
    path("unread/count/", UnreadNotificationCountView.as_view(), name="unread_notification_count"),
]
