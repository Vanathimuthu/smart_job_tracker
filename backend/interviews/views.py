from rest_framework import generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta

from .models import Interview
from .serializers import InterviewSerializer
from .services import send_interview_reminders, get_interviews_needing_reminders


class InterviewListCreateView(generics.ListCreateAPIView):
    serializer_class = InterviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Interview.objects.filter(user=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        
        # Add helpful message about email reminder
        if response.status_code == status.HTTP_201_CREATED:
            interview_data = response.data
            scheduled_at = interview_data.get('scheduled_at')
            
            if scheduled_at:
                try:
                    from datetime import datetime
                    scheduled_time = datetime.fromisoformat(scheduled_at.replace('Z', '+00:00'))
                    now = timezone.now()
                    time_until = (scheduled_time - now).total_seconds()
                    
                    if 0 < time_until <= (24 * 60 * 60):
                        response.data['_message'] = '✓ Email reminder will be sent'
                    elif time_until > (24 * 60 * 60):
                        response.data['_message'] = '✓ Interview saved (reminder will be sent 24 hours before)'
                except:
                    pass
        
        return response


class InterviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = InterviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Interview.objects.filter(user=self.request.user)

