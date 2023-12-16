from django.shortcuts import get_object_or_404
from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Review, Title, User


class AuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'username')


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'confirmation_code')
        extra_kwargs = {
            'username': {
                'validators': []
            }
        }


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категории."""
    class Meta:
        model = Category
        fields = ['name', 'slug']


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанра."""
    class Meta:
        model = Genre
        fields = ['name', 'slug']


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для произведения."""
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True,
        required=False,
    )
    rating = serializers.IntegerField(read_only=True, default=None)

    class Meta:
        model = Title
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментария."""
    author = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        read_only=True,
        slug_field='username'
    )

    class Meta:
        fields = ['id', 'text', 'author', 'pub_date']
        model = Comment


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзыва."""
    author = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        read_only=True,
        slug_field='username'
    )
    score = serializers.IntegerField(max_value=10, min_value=1)

    def validate(self, data):
        """
        Проверка, что пользователь не оставлял отзыв на текущее произведение.
        """
        if self.context['request'].method in ('PUT', 'PATCH'):
            return data

        title_id = self.context['view'].kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        author = self.context['request'].user
        if author.reviews.filter(title=title).exists():
            raise serializers.ValidationError(
                (f'Отзыв к произведению {title.pk} '  # Поменять 'pk' на 'name'
                 f'от пользователя {author.username} уже существует!')
            )
        return data

    class Meta:
        fields = ['id', 'text', 'author', 'score', 'pub_date']
        model = Review
