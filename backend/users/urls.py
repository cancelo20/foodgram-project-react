from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import UserViewSet


router = DefaultRouter()
router.register(r'users', UserViewSet)

subscribe = UserViewSet.as_view(
    {
        'post': 'subscribe',
        'delete': 'unsubscribe',
    }
)

urlpatterns = [
    path('', include(router.urls)),
    path('users/<int:id>/subscribe/', subscribe)
]
