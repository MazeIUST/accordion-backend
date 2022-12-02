from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'', SongViewSet, basename='songs')
router.register(r'tag', TagViewSet, basename='tag')
router.register(r'playlist', PlaylistViewSet, basename='playlist')


urlpatterns = [
    path('', SongViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('<int:pk>/', SongViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),
    path('delete_all/', SongViewSet.as_view({'delete': 'destroy_all', 'get': 'list'})),
    path('search/<str:text>/', SongViewSet.as_view({'get': 'search'}), name='song_search'),

    path('tag/', TagViewSet.as_view({'get': 'list', 'post': 'create'}), name='tags'),
    path('tag/<int:pk>/', TagViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='tag'),

    path('playlist/', PlaylistViewSet.as_view({'post': 'create', 'get': 'list'}), name='playlist'),
    path('playlist/<int:pk>/', PlaylistViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='playlist'),
    path('playlist/add_song/song_id/<int:song_pk>/playlist_id/<int:playlist_pk>/', PlaylistViewSet.as_view({'put': 'add_song'}), name='add_song'),
]