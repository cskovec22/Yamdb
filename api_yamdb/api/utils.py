from django.conf import settings
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken


def send_code_by_mail(email, random_code):
    """Функция отправляет код на электронную почту."""
    send_mail(
        subject="Your confirmation code",
        message=f"{random_code} - confirmation code",
        from_email=settings.USER_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )


def get_tokens_for_user(user):
    """Функция создает токен для пользователя."""
    refresh = RefreshToken.for_user(user)

    return {
        "token": str(refresh.access_token),
    }
