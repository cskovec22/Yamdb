import datetime as dt

# from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


# ROLES = [
#     ('user', 'Пользователь'),
#     ('moderator', 'Модератор'),
#     ('admin', 'Администратор')
# ]


class BaseModel(models.Model):
    """Базовая модель."""
    pub_date = models.DateTimeField(
        'Дата создания',
        auto_now_add=True
    )

    class Meta:
        abstract = True


# User = get_user_model()


# class User(AbstractUser):
#     username = models.CharField(
#         'Имя пользователя',
#         max_length=150,
#         unique=True
#     )
#     first_name = models.CharField(
#         'Имя',
#         max_length=150,
#         blank=True
#     )
#     last_name = models.CharField(
#         'Фамилия',
#         max_length=150,
#         blank=True
#     )
#     email = models.EmailField(
#         'Почта',
#         max_length=254,
#         unique=True
#     )
#     bio = models.TextField('Биография', blank=True)
#     role = models.CharField(
#         'Роль',
#         choices=ROLES,
#         default='user',
#         max_length=len('moderator')
#     )
#     confirmation_code = models.CharField(
#         "Код подтверждения",
#         blank=True,
#         max_length=6,
#         null=True
#     )

#     def is_admin(self):
#         return self.is_staff or self.role == 'admin'

#     class Meta:
#         ordering = ('username', )
#         verbose_name = 'пользователь'
#         verbose_name_plural = 'Пользователи'


class CustomUser(AbstractUser):
    class Users(models.TextChoices):
        USER = "user", _("пользователь")
        MODERATOR = "moderator", _("модератор")
        ADMIN = "admin", _("администратор")

    bio = models.TextField(verbose_name="Биография", null=True, blank=True)
    role = models.TextField(
        verbose_name="Роль",
        choices=Users.choices,
        default=Users.USER
    )
    confirmation_code = models.CharField(
        verbose_name="Код подтверждения",
        max_length=6,
        null=True,
        blank=True
    )


class Category(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Категория и описание'
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
    )

    class Meta:
        ordering = ('name', )
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Жанр и описание'
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
    )

    class Meta:
        ordering = ('name', )
        verbose_name = 'жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Название'
    )
    year = models.IntegerField(db_index=True)
    description = models.TextField(
        verbose_name='Описание',
        blank=True,
        null=True
    )
    genre = models.ManyToManyField(
        Genre,
        through="GenreTitle",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        blank=True,
        null=True,
        verbose_name='Категория'
    )

    class Meta:
        ordering = ('name', )
        verbose_name = 'произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name

    @staticmethod
    def validate(year):
        if dt.datetime.now().year <= year:
            raise ValidationError(
                'Нельзя материалы произведения из будущего!'
            )


class GenreTitle(models.Model):
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title} - {self.genre}"


class Review(BaseModel):
    """Модель отзыва."""
    text = models.TextField('Текст отзыва')
    author = models.ForeignKey(
        CustomUser,
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
        ordering = ('text', )
        verbose_name = 'отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return self.text


class Comment(BaseModel):
    """Модель комментария."""
    text = models.TextField('Текст комментария')
    author = models.ForeignKey(
        CustomUser,
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
        ordering = ('text', )
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text
