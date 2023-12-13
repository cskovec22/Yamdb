from django.shortcuts import get_object_or_404
from rest_framework import viewsets

from api.serializers import ReviewSerializer
from reviews.models import Review, Title


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для просмотра и редактирования отзыва."""
    serializer_class = ReviewSerializer

    def get_title(self):
        """Получает конкретное произведение."""
        title_id = self.kwargs.get('title_id')
        return get_object_or_404(Title, pk=title_id)

    def get_queryset(self):
        """Возвращает queryset c отзывами для конкретного произведения."""
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        """
        Создает отзыв для конкретного произведения, где автор -
        текущий пользователь.
        """
        serializer.save(
            author=self.request.user,
            title=self.get_title()
        )

    def perform_update(self, serializer):
        """
        Редактирует отзыв для конкретного произведения, где автор -
        текущий пользователь.
        """
        serializer.save(
            author=self.request.user,
            title=self.get_title()
        )
