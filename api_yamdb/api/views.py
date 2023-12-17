from random import randint

import jwt
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Category, CustomUser, Genre, Review, Title

from api.filters import TitleFilter
from api.permissions import (IsAdminOnlyPermission,
                             IsAdminOrReadOnlyPermission, RolesPermission)
from api.serializers import (AuthSerializer, CategorySerializer,
                             CommentSerializer, CustomUserSerializer,
                             GenreSerializer, ReviewSerializer,
                             TitleGetSerializer, TitlePostSerializer,
                             TokenSerializer)


class MixinsViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                    mixins.RetrieveModelMixin, mixins.DestroyModelMixin,
                    mixins.UpdateModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAdminOrReadOnlyPermission,)
    http_method_names = ['get', 'post', 'patch', 'delete']


class CustomUserViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminOnlyPermission, )
    queryset = CustomUser.objects.all()
    # filter_backends = (filters.SearchFilter,)
    # search_fields = ('username',)
    serializer_class = CustomUserSerializer
    lookup_field = 'username'


class CategoryViewSet(MixinsViewSet):
    """Вьюсет для просмотра и редактирования категории."""
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name', )
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(MixinsViewSet):
    """Вьюсет для просмотра и редактирования жанра."""
    # permission_classes = (IsAdminOrReadOnlyPermission, )
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name', )
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(MixinsViewSet):
    """Вьюсет для просмотра и редактирования произведения."""
    filterset_class = TitleFilter
    filter_backends = [DjangoFilterBackend]
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    # serializer_class = TitleSerializer

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return TitleGetSerializer
        return TitlePostSerializer


# class GetToken(APIView):
#     # authentication_classes = [authentication.TokenAuthentication]
#     permission_classes = [AllowAny, ]

#     def post(self, request):
#         token_serializer = TokenSerializer(data=request.data)
#         if token_serializer.is_valid(raise_exception=True):
#             try:
#                 user = get_object_or_404(
#                     CustomUser,
#                     username=token_serializer.validated_data['username']
#                 )
#             except CustomUser.DoesNotExist:
#                 return Response(status=status.HTTP_404_NOT_FOUND)
#             print(token_serializer.validated_data)
#             if token_serializer.validated_data[
#                 'confirmation_code'
#             ] == user.confirmation_code:
#                 token_data = {'username': user.username}
#                 token = jwt.encode(token_data,
#                                    str(token_serializer['confirmation_code']),
#                                    algorithm='HS256')
#                 return Response(
#                     {'token': token},
#                     status=status.HTTP_201_CREATED
#                 )
#             return Response(
#                 {'error': 'Invalid confirmation code'},
#                 status=status.HTTP_404_NOT_FOUND
#             )
#         return Response(
#             token_serializer.errors,
#             status=status.HTTP_400_BAD_REQUEST
#         )

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
            user = get_object_or_404(
                CustomUser,
                username=serializer.validated_data.get('username')
            )
            token = get_tokens_for_user(user)
            return Response(token)
        return Response(serializer.errors)


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
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors)


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
