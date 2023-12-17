from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from reviews.models import Category, Comment, CustomUser, Genre, Review, Title


class AuthSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=CustomUser.objects.all())],
        max_length=150
    )
    username = serializers.SlugField(
        validators=[UniqueValidator(queryset=CustomUser.objects.all())],
        max_length=254
    )

    class Meta:
        model = CustomUser
        fields = ('email', 'username')


class Token():
    def init(self, username, confirmation_code):
        self.username = username
        self.confirmation_code = confirmation_code


class TokenSerializer(serializers.Serializer):

    username = serializers.SlugField(max_length=150)
    confirmation_code = serializers.CharField()

    def validate(self, data):
        user = get_object_or_404(CustomUser, username=data['username'])
        if user.confirmation_code != data['confirmation_code']:
            raise serializers.ValidationError("Неправильный код подтверждения!")
        return data


# class TokenSerializer(serializers.ModelSerializer):
#     username = serializers.CharField(max_length=150)
#     confirmation_code = serializers.CharField(max_length=200)

#     class Meta:
#         model = CustomUser
#         fields = ('username', 'confirmation_code')
#         extra_kwargs = {
#             'username': {
#                 'validators': []
#             }
#         }


class CustomUserSerializer(serializers.ModelSerializer):
    def validate_username(self, username):
        """
        Проверяет, что значение поля 'username' не 'me'.
        """
        if username == 'me':
            raise serializers.ValidationError(
                'Данное имя пользователя запрещено!'
            )
        return username

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')


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
        # required=False,
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
