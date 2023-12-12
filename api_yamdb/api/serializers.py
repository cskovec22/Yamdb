from rest_framework import serializers

from reviews.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзыва."""
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        fields = ['id', 'text', 'author', 'score', 'pub_date']
        model = Review
