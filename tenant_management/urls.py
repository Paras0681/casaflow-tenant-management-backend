"""
URL configuration for tenant_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from decouple import config
from django.http import JsonResponse

def frontend_config(request):
    return JsonResponse({
        "API_URL": config("FRONTEND_API_URL", default="http://127.0.0.1:8000/api")
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path("config.json", frontend_config),
    path("api/users/", include("tenant_management.apps.users.urls")),
    path("api/tenants/", include("tenant_management.apps.tenants.urls")),
    path("api/payments/", include("tenant_management.apps.payments.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
