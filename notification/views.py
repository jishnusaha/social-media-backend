# notifications/views.py
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.shortcuts import get_object_or_404

from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Notification.objects.filter(recipient=user)

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response(
            {"detail": "Notification marked as read."}, status=status.HTTP_200_OK
        )

    @action(detail=False, methods=["post"])
    def mark_all_read(self, request):
        user = request.user
        Notification.objects.filter(recipient=user, is_read=False).update(is_read=True)
        return Response(
            {"detail": "All notifications marked as read."}, status=status.HTTP_200_OK
        )

    @action(detail=False, methods=["get"])
    def unread(self, request):
        user = request.user
        queryset = Notification.objects.filter(recipient=user, is_read=False)
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def count_unread(self, request):
        user = request.user
        count = Notification.objects.filter(recipient=user, is_read=False).count()
        return Response({"count": count})
