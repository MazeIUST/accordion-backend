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
    path('playlist/<int:pk>/add_song/', PlaylistViewSet.as_view({'put': 'add_song'}), name='playlist_add_song'),
    path('playlist/<int:pk>/remove_song/', PlaylistViewSet.as_view({'put': 'remove_song'}), name='playlist_remove_song'),
    path('playlist/home/', PlaylistViewSet.as_view({'get': 'get_3_public_playlists'}), name='playlist_home'),
]