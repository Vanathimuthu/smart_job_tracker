from django.urls import path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .views import InterviewDetailView, InterviewListCreateView
from .services import send_interview_reminders


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trigger_interview_reminders(request):
    """
    Trigger sending of interview reminders for all users.
    This endpoint can be called periodically by an external scheduler.
    """
    try:
        send_interview_reminders()
        return Response(
            {'message': 'Interview reminders sent successfully.'},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


urlpatterns = [
    path("", InterviewListCreateView.as_view(), name="interview-list-create"),
    path("<int:pk>/", InterviewDetailView.as_view(), name="interview-detail"),
    path("send-reminders/", trigger_interview_reminders, name="send-reminders"),
]
