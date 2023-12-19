from random import randint

from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken


def get_random_code():
    """Функция создает рандомный пятизначный код из цифр."""
    return str(randint(10000, 99999))


def send_code_by_mail(email, random_code):
    """Функция отправляет код на электронную почту."""
    send_mail(
        subject='Your confirmation code',
        message=f'{random_code} - confirmation code',
        from_email='from@yamdb.com',
        recipient_list=[email],
        fail_silently=False
    )


def get_tokens_for_user(user):
    """Функция создает токен для пользователя."""
    refresh = RefreshToken.for_user(user)

    return {
        'token': str(refresh.access_token),
    }
