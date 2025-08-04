from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema-yaml/", SpectacularAPIView.as_view(), name="schema-yaml"),
    path(
        "api/swagger",
        SpectacularSwaggerView.as_view(url_name="schema-yaml"),
        name="swagger",
    ),
    path("/", include("backend.urls")),
]
