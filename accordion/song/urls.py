from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'artist', SongViewSet_Artist, basename='artist')
router.register(r'user', SongViewSet_User, basename='user')
router.register(r'tag', TagViewSet, basename='tag')


urlpatterns = [
    path('artist/', SongViewSet_Artist.as_view({'get': 'list', 'post': 'create'}), name='songs'),
    path('artist/<int:pk>/', SongViewSet_Artist.as_view({'get': 'retrieve', 'put': 'update'}), name='song'),
    path('artist/<int:pk>/delete/', SongViewSet_Artist.as_view({'delete': 'destroy'}), name='song_delete'),

    path('user/', SongViewSet_User.as_view({'get': 'list'}), name='songs'),
    path('user/<int:pk>/', SongViewSet_User.as_view({'get': 'retrieve'}), name='song'),

    path('tag/', TagViewSet.as_view({'get': 'list', 'post': 'create'}), name='tags'),
    path('tag/<int:pk>/', TagViewSet.as_view({'get': 'retrieve', 'put': 'update'}), name='tag'),
    path('tag/<int:pk>/delete/', TagViewSet.as_view({'delete': 'destroy'}), name='tag_delete'),
]