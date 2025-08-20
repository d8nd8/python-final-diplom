from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartViewSet, ContactViewSet, OrderViewSet
from .views import (
    RegisterView,
    LoginView,
    ConfirmEmailView,
    PartnerUpdateView,
    ProductListView,
    SocialAuthView,
    SocialAuthCallbackView,
    SocialAuthStatusView,
    AvatarUploadView,
    AvatarStatusView,
    SentryTestView,
)

router = DefaultRouter()
router.register(r"cart", CartViewSet, basename="cart")
router.register(r"contacts", ContactViewSet, basename="contacts")
router.register(r"orders", OrderViewSet, basename="orders")

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
    path("social-auth/providers/", SocialAuthView.as_view(), name="social-providers"),
    path("social-auth/status/", SocialAuthStatusView.as_view(), name="social-status"),
    path("social-auth/callback/", SocialAuthCallbackView.as_view(), name="social-callback"),
    path("profile/avatar/upload/", AvatarUploadView.as_view(), name="avatar-upload"),
    path("profile/avatar/status/", AvatarStatusView.as_view(), name="avatar-status"),
    path("test/sentry/", SentryTestView.as_view(), name="sentry-test"),
    path("/", include(router.urls)),
]
