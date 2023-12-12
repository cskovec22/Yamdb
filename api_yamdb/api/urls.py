from django.urls import include, path
from rest_framework import routers

from api.views import ReviewViewSet


app_name = 'api'

router = routers.DefaultRouter()
# router.register(r'groups', GroupViewSet) 
# router.register( 
#     r'posts/(?P<post_id>\d+)/comments', 
#     CommentViewSet, 
#     basename='comments' 
# ) 
router.register(r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet)

urlpatterns = [
    path('v1/', include(router.urls))
]
