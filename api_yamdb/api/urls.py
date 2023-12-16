from django.urls import include, path
from rest_framework import routers

from api.views import (CategoryViewSet, CommentViewSet, GenreViewSet, GetToken,
                       ReviewViewSet, SignUp, TitleViewSet, CustomUserViewSet)


app_name = 'api'

router = routers.DefaultRouter()

router.register(
    r'users',
    CustomUserViewSet,
    basename='users'
)
router.register(
    r'categories',
    CategoryViewSet,
    basename='category'
)
router.register(
    r'genres',
    GenreViewSet,
    basename='genre'
)
router.register(
    r'titles',
    TitleViewSet,
    basename='titles'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/signup/', SignUp.as_view(), name='signup'),
    path('v1/auth/token/', GetToken.as_view(), name='token')
]
