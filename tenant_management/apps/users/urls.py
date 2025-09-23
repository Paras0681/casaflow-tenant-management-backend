from django.urls import path
from .views import LoginAPIView,RegisterAPIView, GetUsersAPIView, ForgetPasswordAPIView, ResetPasswordAPIView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("login/", LoginAPIView.as_view(), name="login"),
    path("register/", RegisterAPIView.as_view(), name="register"),
    path("refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("users/", GetUsersAPIView.as_view(), name="users"),
    path("forgot-password/", ForgetPasswordAPIView.as_view(), name="forgot-password"),
    path("reset-password/<str:token>/", ResetPasswordAPIView.as_view(), name="reset-password"),
]
