from django.urls import path
from .views import AdminUserListView, EndUserListView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh-token", TokenRefreshView.as_view(), name="token_refresh"),
    path("admins/", AdminUserListView.as_view(), name="admin-list"),
    path("end-users/", EndUserListView.as_view(), name="end-user-list"),
]
