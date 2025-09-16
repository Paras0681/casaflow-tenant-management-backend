from django.urls import path
from .views import GetPaymentsAPIView, MarkPaymentsAPIView

urlpatterns = [
    path("get-payments/", GetPaymentsAPIView.as_view(), name="get-payments"),
    path("mark-payments/", MarkPaymentsAPIView.as_view(), name="mark-payments")
]
