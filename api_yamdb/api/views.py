from django.contrib.auth.tokens import default_token_generator
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.views import APIView

from reviews.models import Category, CustomUser, Genre, Review, Title
from api.filters import TitleFilter
from api.permissions import (IsAdminObjectReadOnlyPermission,
                             IsAdminOnlyPermission,
                             IsAdminOrReadOnlyPermission, RolesPermission)
from api.serializers import (AuthSerializer, CategorySerializer,
                             CommentSerializer, CustomUserSerializer,
                             GenreSerializer, ReviewSerializer,
                             TitleGetSerializer, TitlePostSerializer,
                             TokenSerializer)
from api.utils import get_tokens_for_user, send_code_by_mail


class MixinsViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                    mixins.RetrieveModelMixin, mixins.DestroyModelMixin,
                    mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    Вьюсет миксинов для обработки 'get', 'post', 'patch', и 'delete' методов.
    """
    http_method_names = ['get', 'post', 'patch', 'delete']


class SignUp(APIView):
    """APIView для регистрации нового пользователя."""
    permission_classes = (AllowAny, )

    def post(self, request, format=None):
        """
        Создание нового пользователя,
        либо обновление 'confirmation code' для текущего.
        """
        serializer = AuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        email = serializer.validated_data.get('email')
        try:
            user = CustomUser.objects.get(
                username=username,
                email=email
            )
        except CustomUser.DoesNotExist:
            if CustomUser.objects.filter(username=username).exists():
                raise ValidationError(
                    'Пользователь с таким логином уже существует!'
                )
            elif CustomUser.objects.filter(email=email):
                raise ValidationError(
                    'Пользователь с таким email уже существует!'
                )
            user = CustomUser.objects.create(
                username=username,
                email=email
            )
            # user.confirmation_code = get_random_code()
        user.confirmation_code = default_token_generator.make_token(user)
        user.save()
        send_code_by_mail(email, user.confirmation_code)
        return Response(serializer.data, status=status.HTTP_200_OK)


class Token(APIView):
    """APIView для создания токена для конкретного пользователя."""
    permission_classes = (AllowAny,)

    def post(self, request):
        """Получение токена в обмен на 'username' и 'confirmation code'."""
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            CustomUser,
            username=serializer.validated_data.get('username')
        )
        token = get_tokens_for_user(user)
        return Response(token)


class CustomUserViewSet(MixinsViewSet):
    """Вьюсет для просмотра администратором пользователя."""
    filter_backends = (filters.SearchFilter,)
    lookup_field = 'username'
    permission_classes = (IsAdminOnlyPermission,)
    queryset = CustomUser.objects.all()
    search_fields = ('username',)
    serializer_class = CustomUserSerializer


class UsersMeView(APIView):
    """APIView для просмотра или редактирования собственного профиля."""
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        """Получает определенный объект пользователя."""
        serializer = CustomUserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        """Редактирует определенный объект пользователя."""
        serializer = CustomUserSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(role=request.user.role)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryViewSet(MixinsViewSet):
    """Вьюсет для просмотра и редактирования категории."""
    http_method_names = ['get', 'post', 'delete']
    filter_backends = (filters.SearchFilter,)
    lookup_field = 'slug'
    permission_classes = (IsAdminObjectReadOnlyPermission,)
    queryset = Category.objects.all()
    search_fields = ('name',)
    serializer_class = CategorySerializer

    def retrieve(self, request, *args, **kwargs):
        """Запрещает просмотр определённой категории."""
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class GenreViewSet(viewsets.ModelViewSet):
    """Вьюсет для просмотра и редактирования жанра."""
    http_method_names = ['get', 'post', 'delete']
    filter_backends = (filters.SearchFilter,)
    lookup_field = 'slug'
    permission_classes = (IsAdminObjectReadOnlyPermission,)
    search_fields = ('name',)
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()

    def retrieve(self, request, *args, **kwargs):
        """Запрещает просмотр определённого жанра."""
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class TitleViewSet(MixinsViewSet):
    """Вьюсет для просмотра и редактирования произведения."""
    filterset_class = TitleFilter
    filter_backends = [DjangoFilterBackend]
    permission_classes = (IsAdminOrReadOnlyPermission,)
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))

    def get_serializer_class(self):
        """Определяет класс сериализатора в зависимости от метода."""
        if self.request.method in permissions.SAFE_METHODS:
            return TitleGetSerializer
        return TitlePostSerializer


class CommentViewSet(MixinsViewSet):
    """Вьюсет для просмотра и редактирования комментария."""
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthenticatedOrReadOnly, RolesPermission,)
    serializer_class = CommentSerializer

    def get_review(self):
        """Получает конкретный отзыв."""
        review_id = self.kwargs.get('review_id')
        title_id = self.kwargs.get('title_id')
        return get_object_or_404(Review, pk=review_id, title_id=title_id)

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
