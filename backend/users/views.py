from rest_framework import permissions, viewsets
from rest_framework.response import Response

from .models import CustomUser
from .permissions import IsLoggedInUserOrStaff, IsStaffUser
from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API view for interacting with users
    """

    # only admin users should be allowed to view the user list
    permission_classes = [permissions.IsAdminUser]
    queryset = CustomUser.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer

    def create(self, request):
        """
        We don't allow creation through this view,
        use /api/auth/register/ instead
        """
        return Response(
            "This endpoint does not allow for registration, use /api/auth/register/ instead.",
            status=405,
        )

    def get_permissions(self):
        """
        Enforce different permissions per request types
        """
        permission_classes = []
        # noone should be able to post to this view
        # (registration is done with DRR)
        if self.action == "create":
            permission_classes = []
        # only the logged in user or a staff member should be able to:
        # get, update their credentials
        elif (
            self.action == "retrieve"
            or self.action == "update"
            or self.action == "partial_update"
        ):
            permission_classes = [IsLoggedInUserOrStaff]
        # only the admin can list all users or remove users
        elif self.action == "list" or self.action == "destroy":
            permission_classes = [IsStaffUser]
        return [permission() for permission in permission_classes]
