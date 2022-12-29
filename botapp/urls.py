from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import *
from song.views import SongViewSet


urlpatterns = [
    path('signup/<str:chat_id>/', UserViewSet.as_view({'get': 'signup'})),
    path('start/<int:chat_id>/', UserViewSet.as_view({'get': 'start'})),
    path('get_song/<int:song_id>/', UserViewSet.as_view({'get': 'get_song'})),
    path('search/<str:text>/', SongViewSet.as_view({'get': 'search'})),
]