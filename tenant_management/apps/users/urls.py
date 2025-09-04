from django.urls import path
from .views import LoginAPIView,RegisterAPIView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("login/", LoginAPIView.as_view(), name="login"),
    path("register/", RegisterAPIView.as_view(), name="register"),
    path("refresh/", TokenRefreshView.as_view(), name="refresh"),
]
