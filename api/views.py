# api/views.py
from rest_framework import viewsets
from core.models import UserProfile, JobPost
from .serializers import UserProfileSerializer, JobPostSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from core.tasks import career_planner_agent

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    @action(detail=True, methods=['post'])
    def generate_roadmap(self, request, pk=None):
        user = self.get_object()
        # enqueue agent
        career_planner_agent.delay(request.user.email if request.user.is_authenticated else "anonymous", user.id)
        return Response({"status":"queued"})

class JobPostViewSet(viewsets.ModelViewSet):
    queryset = JobPost.objects.all()
    serializer_class = JobPostSerializer
