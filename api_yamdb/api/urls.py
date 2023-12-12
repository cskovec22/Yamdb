from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import (CategoryViewSet,
                    GenreViewSet,
                    TitleViewSet)

router = DefaultRouter()
router.register(r'category', CategoryViewSet, basename='category')
router.register(r'genres', GenreViewSet, basename='genre')
router.register(r'titles', TitleViewSet, basename='title')

urlpatterns = [
    path('api/v1/', include(router.urls)),
]
