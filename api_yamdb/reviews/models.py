import datetime as dt

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _


MIN_VALUE_SCORE = 1
MAX_VALUE_SCORE = 10


class BaseModel(models.Model):
    """Базовая модель."""

    pub_date = models.DateTimeField("Дата создания", auto_now_add=True)

    class Meta:
        abstract = True


class CustomUser(AbstractUser):
    """Кастомная модель юзера."""

    class Roles(models.TextChoices):
        USER = ("user", _("Пользователь"))
        MODERATOR = ("moderator", _("Модератор"))
        ADMIN = ("admin", _("Администратор"))

    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[username_validator],
        verbose_name="Имя пользователя",
        help_text="Введите уникальный логин, не более 150 символов",
    )
    first_name = models.CharField(
        blank=True,
        max_length=150,
        verbose_name="Имя",
        help_text="Введите имя, не более 150 символов",
    )
    last_name = models.CharField(
        blank=True,
        max_length=150,
        verbose_name="Фамилия",
        help_text="Введите фамилию, не более 150 символов",
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name="Почта",
        help_text="Введите email, не более 254 символа",
    )
    bio = models.TextField(blank=True, verbose_name="Биография")
    role = models.CharField(
        choices=Roles.choices,
        default="user",
        max_length=len(Roles.MODERATOR),
        verbose_name="Роль",
    )

    class Meta:
        ordering = ("username",)
        verbose_name = "пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == self.Roles.ADMIN or self.is_staff

    @property
    def is_moderator(self):
        return self.role == self.Roles.MODERATOR


class Category(models.Model):
    """Модель категории."""

    name = models.CharField(
        max_length=256, unique=True, verbose_name="Категория и описание"
    )
    slug = models.SlugField(
        max_length=50, unique=True, verbose_name="slug категории"
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Genre(models.Model):
    """Модель жанра."""

    name = models.CharField(
        max_length=256, unique=True, verbose_name="Жанр и описание"
    )
    slug = models.SlugField(
        max_length=50, unique=True, verbose_name="slug жанра"
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "жанр"
        verbose_name_plural = "Жанры"

    def __str__(self):
        return self.name


class Title(models.Model):
    """Модель произведения."""

    name = models.CharField(
        help_text="Введите название произведения, не более 256 символов",
        max_length=256,
        verbose_name="Название",
    )
    year = models.PositiveSmallIntegerField(db_index=True, verbose_name="Год")
    description = models.TextField(
        blank=True, null=True, verbose_name="Описание"
    )
    genre = models.ManyToManyField(
        Genre, through="GenreTitle", verbose_name="Жанр"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name="titles",
        null=True,
        verbose_name="Категория",
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "произведение"
        verbose_name_plural = "Произведения"

    def __str__(self):
        return self.name

    @staticmethod
    def validate(year):
        if dt.datetime.now().year <= year:
            raise ValidationError(
                "Нельзя выкладывать материалы произведения из будущего!"
            )


class GenreTitle(models.Model):
    """Модель, связывающая произведения и жанры."""

    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, verbose_name="Произведение"
    )
    genre = models.ForeignKey(
        Genre, on_delete=models.CASCADE, verbose_name="Жанр"
    )

    class Meta:
        ordering = ("title",)
        verbose_name = "произведение-жанр"
        verbose_name_plural = "Произведения-жанры"

    def __str__(self):
        return f"{self.title} - {self.genre}"


class Review(BaseModel):
    """Модель отзыва."""

    text = models.TextField("Текст отзыва")
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Автор отзыва",
    )
    score = models.PositiveSmallIntegerField(
        "Оценка",
        validators=[
            MinValueValidator(MIN_VALUE_SCORE),
            MaxValueValidator(MAX_VALUE_SCORE),
        ],
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Произведение",
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=("author", "title"),
                name="review_author_title_unique",
            ),
        )
        ordering = ("-pub_date",)
        verbose_name = "отзыв"
        verbose_name_plural = "Отзывы"

    def __str__(self):
        return self.text


class Comment(BaseModel):
    """Модель комментария."""

    text = models.TextField("Текст комментария")
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Автор комментария",
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Отзыв",
    )

    class Meta:
        ordering = ("-pub_date",)
        verbose_name = "комментарий"
        verbose_name_plural = "Комментарии"

    def __str__(self):
        return self.text
