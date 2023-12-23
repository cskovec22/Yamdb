from datetime import datetime

from django.contrib.auth.tokens import default_token_generator
from django.core.validators import MaxValueValidator
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from reviews.models import (
    MAX_VALUE_SCORE,
    MIN_VALUE_SCORE,
    Category,
    Comment,
    CustomUser,
    Genre,
    Review,
    Title,
)


class AuthSerializer(serializers.ModelSerializer):
    """Сериализатор для системы регистрации и аутентификации."""

    email = serializers.EmailField(max_length=254)
    username = serializers.SlugField(max_length=150)

    class Meta:
        fields = ("username", "email")
        model = CustomUser

    def validate_username(self, value):
        """Проверяет, что значение поля 'username' не 'me'."""
        if value == "me":
            raise serializers.ValidationError(
                "Данное имя пользователя запрещено!"
            )
        return value


class TokenSerializer(serializers.Serializer):
    """Сериализатор для токена."""

    username = serializers.SlugField(max_length=150)
    confirmation_code = serializers.CharField()

    def validate(self, data):
        """Проверяет, что переданный код совпадает с кодом пользователя."""
        user = get_object_or_404(CustomUser, username=data["username"])
        confirmation_code = data["confirmation_code"]
        if not default_token_generator.check_token(user, confirmation_code):
            raise serializers.ValidationError(
                "Неправильный код подтверждения!"
            )
        return data


class CustomUserSerializer(serializers.ModelSerializer):
    """Сериализатор для кастомного пользователя."""

    role = serializers.ChoiceField(choices=CustomUser.Roles, default="user")

    class Meta:
        model = CustomUser
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "role",
        )

    def validate_username(self, username):
        """
        Проверяет, что значение поля 'username' не 'me'.
        """
        if username == "me":
            raise serializers.ValidationError(
                "Данное имя пользователя запрещено!"
            )
        return username


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категории."""

    class Meta:
        model = Category
        fields = ["name", "slug"]


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанра."""

    class Meta:
        model = Genre
        fields = ["name", "slug"]


class TitleGetSerializer(serializers.ModelSerializer):
    """Сериализатор для произведения."""

    category = CategorySerializer()
    genre = GenreSerializer(many=True)
    rating = serializers.IntegerField()

    class Meta:
        fields = "__all__"
        model = Title
        read_only_fields = ["__all__"]


class TitlePostSerializer(serializers.ModelSerializer):
    """Сериализатор для создания произведения."""

    category = serializers.SlugRelatedField(
        slug_field="slug",
        queryset=Category.objects.all(),
    )
    genre = serializers.SlugRelatedField(
        slug_field="slug",
        queryset=Genre.objects.all(),
        many=True,
    )
    year = serializers.IntegerField(
        validators=[MaxValueValidator(datetime.now().year)]
    )

    class Meta:
        model = Title
        fields = "__all__"


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментария."""

    author = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        read_only=True,
        slug_field="username",
    )

    class Meta:
        fields = ["id", "text", "author", "pub_date"]
        model = Comment


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзыва."""

    author = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        read_only=True,
        slug_field="username",
    )
    score = serializers.IntegerField(
        min_value=MIN_VALUE_SCORE, max_value=MAX_VALUE_SCORE
    )

    def validate(self, data):
        """
        Проверяет, что пользователь не оставлял отзыв на текущее произведение.
        """
        if self.context["request"].method in ("PUT", "PATCH"):
            return data

        title_id = self.context["view"].kwargs.get("title_id")
        title = get_object_or_404(Title, pk=title_id)
        author = self.context["request"].user
        if author.reviews.filter(title=title).exists():
            raise serializers.ValidationError(
                (
                    f"Отзыв к произведению {title.name} "
                    f"от пользователя {author.username} уже существует!"
                )
            )
        return data

    class Meta:
        fields = ["id", "text", "author", "score", "pub_date"]
        model = Review
