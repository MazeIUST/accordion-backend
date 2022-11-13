import imp
from django.urls import path
from .views import SongViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'songs', SongViewSet, basename='songs')


urlpatterns = [
    path('', SongViewSet.as_view({'get': 'list', 'post': 'create'}), name='songs'),
    path('<int:pk>/', SongViewSet.as_view({'get': 'retrieve', 'put': 'update'}), name='song'),
    path('<int:pk>/delete/', SongViewSet.as_view({'delete': 'destroy'}), name='song_delete'),
]