from django.urls import path
from .views import TenantsProfilesAPIView

urlpatterns = [
    path("tenants-profile/", TenantsProfilesAPIView.as_view(), name="tenants-profile"),
    path("tenants-profile/<uuid:account_id>/", TenantsProfilesAPIView.as_view(), name="tenants-profile-detail"),
]
