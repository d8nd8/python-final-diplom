from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("", RedirectView.as_view(url="admin/", permanent=False)),
    path("admin/", admin.site.urls),
    path("api/schema-yaml/", SpectacularAPIView.as_view(), name="schema-yaml"),
    path(
        "api/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema-yaml"),
        name="swagger",
    ),
    path("api/", include("backend.urls")),
    path("social-auth/", include("social_django.urls", namespace="social")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
