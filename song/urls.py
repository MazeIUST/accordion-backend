from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'', SongViewSet, basename='songs')
router.register(r'tag', TagViewSet, basename='tag')
router.register(r'playlist', PlaylistViewSet, basename='playlist')


urlpatterns = [
    path('', SongViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('<int:pk>/',
         SongViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),
    path('delete_all/',
         SongViewSet.as_view({'delete': 'destroy_all', 'get': 'list'})),
    path('search/<str:text>/',
         SongViewSet.as_view({'get': 'search'}), name='song_search'),
    path('send_to_telegram/<int:pk>/',
         SongViewSet.as_view({'get': 'send_to_telegram'}), name='send_to_telegram'),
    path('get_top_5_songs/', SongViewSet.as_view(
         {'get': 'top_5_artist_song'}), name='get_top_5_artist_song'),
    path('get_top_5_songs/<int:pk>/', SongViewSet.as_view(
         {'get': 'top_5_artist_song'}), name='get_top_5_artist_song_by_id'),

    path(
        'tag/', TagViewSet.as_view({'get': 'list', 'post': 'create'}), name='tags'),
    path('tag/<int:pk>/', TagViewSet.as_view(
        {'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='tag'),

    path('playlist/',
         PlaylistViewSet.as_view({'post': 'create', 'get': 'list'}), name='playlist'),
    path('playlist/<int:pk>/', PlaylistViewSet.as_view(
        {'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='get_playlist'),
    path('playlist/<int:pk>/add_song/', PlaylistViewSet.as_view(
        {'post': 'add_song', 'get': 'retrieve'}), name='playlist_add_song'),
    path('playlist/<int:playlist_pk>/remove_song/<int:song_pk>/',
         PlaylistViewSet.as_view({'delete': 'remove_song'}), name='playlist_remove_song'),
    path('playlist/home/',
         PlaylistViewSet.as_view({'get': 'get_3_public_playlists'}), name='playlist_home'),

    path('album/',
         AlbumViewSet.as_view({'get': 'list', 'post': 'create'}), name='album'),
    path('album/<int:pk>/', AlbumViewSet.as_view(
        {'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='get_album'),
    path('album/<int:pk>/add_song/', AlbumViewSet.as_view(
        {'post': 'add_song', 'get': 'retrieve'}), name='album_add_song'),
    path('album/<int:album_pk>/remove_song/<int:song_pk>/',
         AlbumViewSet.as_view({'delete': 'remove_song'}), name='album_remove_song'),

    path('history/',
         SongLogsViewSet.as_view({'post': 'create', 'get': 'list'}), name='history'),
    path('history/<int:pk>/', SongLogsViewSet.as_view(
        {'get': 'retrieve'}), name='get_history'),
    path('history/song/<int:song_pk>/',
         SongLogsViewSet.as_view({'get': 'retrieve_by_song'}), name='history_retrieve_by_song'),
    path('history/artist/<int:artist_pk>/',
         SongLogsViewSet.as_view({'get': 'retrieve_by_artist'}), name='history_retrieve_by_artist'),
    path('history/user/<int:user_pk>/',
         SongLogsViewSet.as_view({'get': 'retrieve_by_user'}), name='history_retrieve_by_user'),
    path('analysis/<int:days>/<str:city>/<str:country>/<int:min_age>/<int:max_age>/',
         SongLogsViewSet.as_view({'get': 'analysis_tags'})),
    path('analysis_atrist/<int:days>/<str:city>/<str:country>/<int:min_age>/<int:max_age>/',
         SongLogsViewSet.as_view({'get': 'analysis_artists'})),
]
