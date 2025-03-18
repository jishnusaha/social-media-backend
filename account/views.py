from rest_framework import generics
from .models import AdminUser, EndUser
from .serializers import AdminUserSerializer, EndUserSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser


# Admin User Views
class AdminUserListView(generics.ListAPIView):
    queryset = AdminUser.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class EndUserListView(generics.ListAPIView):
    queryset = EndUser.objects.all()
    serializer_class = EndUserSerializer
    permission_classes = [IsAuthenticated]
