from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

import jwt

from reviews.models import Category, Genre, Title, User
from .filters import TitleFilter
from .permissions import IsAdminOrReadOnly
from .serializers import (AuthSerializer,
                          CategorySerializer,
                          GenreSerializer,
                          TitleSerializer,
                          TokenSerializer)


class CategoryViewSet(viewsets.ModelViewSet):
    """Вьюсет для просмотра и редактирования категорий."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]


class GenreViewSet(viewsets.ModelViewSet):
    """Вьюсет для просмотра и редактирования жанров."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrReadOnly]


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для просмотра и редактирования произведений."""
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    serializer_class = TitleSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter


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
