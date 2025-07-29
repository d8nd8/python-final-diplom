from django.utils import timezone
from .models import EmailConfirmToken


def confirm_email(token_key: str):
    """Удаляет токен подтверждения электронной почты и активирует пользователя."""
    try:
        token = EmailConfirmToken.objects.get(token=token_key)
    except EmailConfirmToken.DoesNotExist:
        raise ValueError("Invalid token")

    if hasattr(token, 'is_expired') and token.is_expired:
        token.delete()
        raise ValueError("Token expired")

    user = token.user
    user.is_active = True
    user.save()

    token.delete()
    return user
