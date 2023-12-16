from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

import jwt

from api.filters import TitleFilter
from api.permissions import IsAdminPermission, RolesPermission
from api.serializers import (AuthSerializer,
                             CategorySerializer,
                             CommentSerializer,
                             GenreSerializer,
                             ReviewSerializer,
                             TitleSerializer,
                             TokenSerializer)
from reviews.models import Category, Genre, Review, Title, User


class CategoryViewSet(viewsets.ModelViewSet):
    """Вьюсет для просмотра и редактирования категории."""
    permission_classes = (IsAuthenticatedOrReadOnly, IsAdminPermission, )
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(viewsets.ModelViewSet):
    """Вьюсет для просмотра и редактирования жанра."""
    permission_classes = (IsAuthenticatedOrReadOnly, IsAdminPermission, )
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для просмотра и редактирования произведения."""
    filterset_class = TitleFilter
    filter_backends = [DjangoFilterBackend]
    permission_classes = (IsAuthenticatedOrReadOnly, IsAdminPermission, )
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    serializer_class = TitleSerializer


class GetToken(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        token_serializer = TokenSerializer(data=request.data)
        if token_serializer.is_valid(raise_exception=True):
            try:
                user = get_object_or_404(
                    User,
                    username=token_serializer.validated_data['username']
                )
            except User.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            if token_serializer.validated_data['confirmation_code'
                                               ] == user.confirmation_code:
                token = jwt.encode(AuthSerializer,
                                   token_serializer['confirmation_code'],
                                   algorithm='HS256')
                return Response(
                    {'token': token},
                    status=status.HTTP_201_CREATED
                )
            return Response(
                token_serializer.errors,
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(
            token_serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
            )

      
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
