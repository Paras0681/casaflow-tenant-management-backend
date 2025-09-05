from django.urls import path
from .views import TenantsProfilesAPIView, TenantsFilesAPIView

urlpatterns = [
    path("tenants-profile/", TenantsProfilesAPIView.as_view(), name="tenants-profile"),
    path("tenants-profile/<uuid:account_id>/", TenantsProfilesAPIView.as_view(), name="tenants-profile-detail"),
    path("files/upload/", TenantsFilesAPIView.as_view(), name="upload-tenant-file"),
]
