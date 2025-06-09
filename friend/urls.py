from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"friendship", views.FriendshipViewSet, basename="friendship")
router.register(r"requests", views.FriendRequestViewSet, basename="friend-request")

urlpatterns = [
    path("", include(router.urls)),
]
