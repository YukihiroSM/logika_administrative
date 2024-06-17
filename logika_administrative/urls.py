from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("logika_general.urls", namespace="logika_general")),
    path("", include("logika_auth.urls")),
    path(
        "logika-teachers/", include("logika_teachers.urls", namespace="logika_teachers")
    ),
    path("", include("logika_statistics.urls", namespace="logika_statistics")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
