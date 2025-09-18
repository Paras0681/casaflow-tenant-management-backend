from django.urls import path
from .views import (
    TenantsProfilesAPIView, 
    TenantsFilesAPIView, 
    TenantsFilesListAPIView, 
    GetReceiptsAPIView, 
    GenerateReceiptsAPIView, 
    PropertyAPIView, 
    RoomAPIView,
    DataAnalyticsView,
    YearlyDataView,
    MarkInvoiceAPIView
)

urlpatterns = [
    path("tenants-profile/", TenantsProfilesAPIView.as_view(), name="tenants-profile"),
    path("tenants-profile/<uuid:account_id>/", TenantsProfilesAPIView.as_view(), name="tenants-profile-detail"),
    path("files/upload/", TenantsFilesAPIView.as_view(), name="upload-tenant-file"),
    path("files/", TenantsFilesListAPIView.as_view(), name="fetch-tenant-files"),
    path("files/<int:id>/", TenantsFilesListAPIView.as_view(), name="fetch-tenant-files"),
    path("receipts/", GetReceiptsAPIView.as_view(), name="receipts"),
    path("receipts/generate/", GenerateReceiptsAPIView.as_view(), name="generate-receipts"),
    path("properties/", PropertyAPIView.as_view(), name="properties"),
    path("rooms/", RoomAPIView.as_view(), name="rooms"),
    path("analytics-summary/", DataAnalyticsView.as_view(), name='analytics-summary'),
    path("yearlydata/", YearlyDataView.as_view(), name='yearlydata'),
    path("mark-invoice/", MarkInvoiceAPIView.as_view(), name="mark-invoice")
]
