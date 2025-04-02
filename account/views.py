from rest_framework import generics
from .models import AdminUser, EndUser
from .serializers import (
    AdminUserSerializer,
    EndUserSerializer,
    EndUserRegistrationSerializer,
)
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class EndUserRegistrationView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = EndUserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "EndUser registered successfully!"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminUserListView(generics.ListAPIView):
    queryset = AdminUser.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class EndUserListView(generics.ListAPIView):
    queryset = EndUser.objects.all()
    serializer_class = EndUserSerializer
    permission_classes = [IsAuthenticated]
