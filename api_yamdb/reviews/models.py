from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

User = get_user_model()


# class CustomUser(AbstractUser):
#     """Кастомная модель пользователя."""
#     class Users(models.TextChoices):
#         USER = "user", _("пользователь")
#         MODERATOR = "moderator", _("модератор")
#         ADMIN = "admin", _("администратор")

    # bio = models.TextField(verbose_name="Биография", null=True, blank=True)
    # role = models.TextField(
    #     verbose_name="Роль",
    #     choices=Users.choices,
    #     default=Users.USER
    # )
    # confirmation_code = models.CharField(
    #     verbose_name="Код подтверждения",
    #     max_length=6,
    #     null=True,
    #     blank=True
    # )


class BaseModel(models.Model):
    """Базовая модель."""
    pub_date = models.DateTimeField(
        'Дата создания',
        auto_now_add=True
    )

    class Meta:
        abstract = True


class Title(models.Model):
    pass


class Review(BaseModel):
    """Модель отзыва."""
    text = models.TextField('Текст отзыва')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор отзыва'
    )
    score = models.PositiveSmallIntegerField(
        'Оценка',
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('author', 'title'),
                name='review_author_title_unique',
            ),
        )
        verbose_name = 'отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return self.text


class Comment(BaseModel):
    """Модель комментария."""
    text = models.TextField('Текст комментария')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария'
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text
