from random import randint

import jwt
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Category, CustomUser, Genre, Review, Title

from api.filters import TitleFilter
from api.permissions import (IsAdminOnlyPermission, IsAdminObjectReadOnlyPermission,
                             IsAdminOrReadOnlyPermission, RolesPermission)
from api.serializers import (AuthSerializer, CategorySerializer,
                             CommentSerializer, CustomUserSerializer,
                             GenreSerializer, ReviewSerializer,
                             TitleGetSerializer, TitlePostSerializer,
                             TokenSerializer)


class MixinsViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                    mixins.RetrieveModelMixin, mixins.DestroyModelMixin,
                    mixins.UpdateModelMixin, viewsets.GenericViewSet):
    # permission_classes = (IsAdminOrReadOnlyPermission, )
    http_method_names = ['get', 'post', 'patch', 'delete']


class SignUp(APIView):
    permission_classes = (permissions.AllowAny, )

    def post(self, request, format=None):
        serializer = AuthSerializer(data=request.data)
        if serializer.is_valid():
            confirmation_code = randint(10000, 99999)
            send_mail(
                subject='Your confirmation code',
                message=f'{confirmation_code} - confirmation code',
                from_email='from@yamdb.com',
                recipient_list=[serializer.validated_data.get('email')],
                fail_silently=False,
            )
            serializer.save(confirmation_code=confirmation_code)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'token': str(refresh.access_token),
    }


class Token(APIView):
    permission_classes = [AllowAny,]

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        if serializer.is_valid():
            user = get_object_or_404(CustomUser, username=serializer.validated_data.get('username'))
            token = get_tokens_for_user(user)
            return Response(token)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomUserViewSet(MixinsViewSet):
    filter_backends = (filters.SearchFilter, )
    permission_classes = (IsAdminOnlyPermission, )
    queryset = CustomUser.objects.all()
    search_fields = ('username',)
    serializer_class = CustomUserSerializer
    lookup_field = 'username'


class UsersMeView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = CustomUser.objects.get(username=request.user.username)
        serializer = CustomUserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        user = CustomUser.objects.get(username=request.user.username)
        serializer = CustomUserSerializer(
            user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save(role=request.user.role)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategorySlugView(APIView):
    permission_classes = (IsAdminOnlyPermission,)

    def delete(self, request, category):
        category_obj = get_object_or_404(Category, slug=category)
        category_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CategoryViewSet(MixinsViewSet):
    """Вьюсет для просмотра и редактирования категории."""
    filter_backends = (filters.SearchFilter, )
    # lookup_field = 'slug'
    permission_classes = (IsAdminObjectReadOnlyPermission, )
    search_fields = ('name', )
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreSlugView(APIView):
    permission_classes = (IsAdminOnlyPermission,)

    def delete(self, request, genre):
        genre_obj = get_object_or_404(Genre, slug=genre)
        genre_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GenreViewSet(MixinsViewSet):
    """Вьюсет для просмотра и редактирования жанра."""
    filter_backends = (filters.SearchFilter, )
    # lookup_field = 'slug'
    permission_classes = (IsAdminObjectReadOnlyPermission, )
    search_fields = ('name', )
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(MixinsViewSet):
    """Вьюсет для просмотра и редактирования произведения."""
    filterset_class = TitleFilter
    filter_backends = [DjangoFilterBackend]
    permission_classes = (IsAdminOrReadOnlyPermission, )
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    # serializer_class = TitleSerializer

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return TitleGetSerializer
        return TitlePostSerializer


class CommentViewSet(MixinsViewSet):
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


class ReviewViewSet(MixinsViewSet):
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
