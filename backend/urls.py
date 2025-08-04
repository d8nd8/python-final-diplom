from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    ConfirmEmailView,
    PartnerUpdateView,
    ProductListView,
)

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/confirm-email/", ConfirmEmailView.as_view(), name="auth-confirm-email"),
    path(
        "partner/upload-product-list",
        PartnerUpdateView.as_view(),
        name="partner-upload-product-list",
    ),
    path("products/", ProductListView.as_view(), name="product-list"),
]
