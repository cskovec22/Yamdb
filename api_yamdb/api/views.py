from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import viewsets

from api.serializers import (
    CommentSerializer, ReviewSerializer, TitleSerializer
)
from api.permissions import IsAdminPermission, RolesPermission
from reviews.models import Review, Title


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для просмотра и редактирования комментария."""
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthenticatedOrReadOnly, RolesPermission, )
    serializer_class = CommentSerializer

    def get_review(self):
        """Получает конкретный отзыв."""
        review_id = self.kwargs.get('review_id')
        return get_object_or_404(Review, pk=review_id)

    def get_queryset(self):
        """Возвращает queryset c комментариями для конкретного отзыва."""
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        """
        Создает комментарий для конкретного отзыва, где автор -
        текущий пользователь.
        """
        serializer.save(
            author=self.request.user,
            review=self.get_review()
        )

    def perform_update(self, serializer):
        """
        Редактирует комментарий для конкретного отзыва, где автор -
        текущий пользователь.
        """
        serializer.save(
            author=self.request.user,
            review=self.get_review()
        )


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для просмотра и редактирования отзыва."""
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthenticatedOrReadOnly, RolesPermission, )
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


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для просмотра и редактирования произведения."""
    permission_classes = (IsAuthenticatedOrReadOnly, IsAdminPermission, )
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    serializer_class = TitleSerializer
