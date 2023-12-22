from django.urls import include, path
from rest_framework import routers

from api.views import (
    CategoryViewSet,
    CommentViewSet,
    CustomUserViewSet,
    GenreViewSet,
    ReviewViewSet,
    SignUp,
    TitleViewSet,
    Token,
    UsersMeView,
)


app_name = "api"

router = routers.DefaultRouter()

router.register(r"users", CustomUserViewSet, basename="users")
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"genres", GenreViewSet, basename="genre")
router.register(r"titles", TitleViewSet, basename="titles")
router.register(
    r"titles/(?P<title_id>\d+)/reviews", ReviewViewSet, basename="reviews"
)
router.register(
    r"titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments",
    CommentViewSet,
    basename="comments",
)

url_auth = [
    path("signup/", SignUp.as_view(), name="signup"),
    path("token/", Token.as_view(), name="token"),
]

urlpatterns = [
    path("v1/users/me/", UsersMeView.as_view(), name="users_me"),
    path("v1/auth/", include(url_auth)),
    path("v1/", include(router.urls)),
]
