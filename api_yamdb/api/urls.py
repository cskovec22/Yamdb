from django.urls import include, path
from rest_framework import routers

from api.views import (CategoryViewSet, CommentViewSet, CustomUserViewSet,
                       GenreViewSet, ReviewViewSet, SignUp, TitleViewSet,
                       UsersMeView, Token, GenreSlugView, CategorySlugView)


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
    path('v1/categories/<slug:category>/', CategorySlugView.as_view(), name='category_slug_delete'),
    path('v1/genres/<slug:genre>/', GenreSlugView.as_view(), name='genre_slug_delete'),
    path('v1/users/me/', UsersMeView.as_view(), name='users_me'),
    path('v1/', include(router.urls)),
    path('v1/auth/signup/', SignUp.as_view(), name='signup'),
    path('v1/auth/token/', Token.as_view(), name='token')
]
