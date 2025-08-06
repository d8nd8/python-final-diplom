from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartViewSet
from .views import (
    RegisterView,
    LoginView,
    ConfirmEmailView,
    PartnerUpdateView,
    ProductListView,
)

router = DefaultRouter()
router.register(r"cart", CartViewSet, basename="cart")


urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/confirm-email/", ConfirmEmailView.as_view(), name="auth-confirm-email"),
    path(
        "partner/list-upload",
        PartnerUpdateView.as_view(),
        name="partner-upload-product-list",
    ),
    path("products/", ProductListView.as_view(), name="product-list"),
    path("/", include(router.urls)),
]
