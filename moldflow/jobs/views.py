from rest_framework import viewsets

from .models import Job
from users.permissions import IsLoggedInUserOrAdmin
from .serializers import JobSerializer


class JobView(viewsets.ModelViewSet):
    permission_classes = [IsLoggedInUserOrAdmin]
    serializer_class = JobSerializer
    queryset = Job.objects.all().order_by("-created")

    def get_queryset(self):
        """
        This view should return a list of all the todos
        for the currently authenticated user or staff
        """
        user = self.request.user

        if user.is_authenticated:
            if user.is_staff:
                return Job.objects.all()
            else:
                return Job.objects.filter(owner=user)

    def perform_create(self, serializer):
        user = self.request.user

        if user.is_authenticated:
            serializer.save(owner=self.request.user)