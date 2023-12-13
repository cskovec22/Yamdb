from django.shortcuts import get_object_or_404
from rest_framework import serializers

from reviews.models import Comment, Review, Title


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

    class Meta:
        fields = ['id', 'text', 'author', 'score', 'pub_date']
        model = Review
