"""
URL configuration for logika_administrative project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from logika_general import views as logika_general_views
from logika_administrative.settings import ADMIN_ENABLED

urlpatterns = [
    path("/", include("logika_general.urls", namespace="logika_general")),
    path("/", include("logika_auth.urls")),
    path("logika-teachers/", include("logika_teachers.urls", namespace="logika_teachers")),
    path("/", include("logika_statistics.urls", namespace="logika_statistics")),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if ADMIN_ENABLED:
    urlpatterns += [path("admin/", admin.site.urls),]

handler404 = logika_general_views.error_404
handler500 = logika_general_views.error_500
