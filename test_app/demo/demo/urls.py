from django.conf.urls import url, include
from djforge_redis_multitokens.tokens_auth import CachedTokenAuthentication
from rest_framework import routers

from quickstart import views
from tests.utils import MockView


router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)


urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url( r'^token/$', MockView.as_view(authentication_classes=[CachedTokenAuthentication])),
]
