from django.urls import path

from .views import NotificationDetailView, NotificationListCreateView

urlpatterns = [
    path("", NotificationListCreateView.as_view(), name="notification-list-create"),
    path("<int:pk>/", NotificationDetailView.as_view(), name="notification-detail"),
]
