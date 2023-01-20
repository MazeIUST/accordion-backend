from django.urls import path
from .views import *


urlpatterns = [
    path('add_song/',
         SongViewSet.as_view({'post': 'create'}), name='add_song'),
    path('download_song/<int:pk>/',
         SongViewSet.as_view({'get': 'download_song'}), name='download_song'),
]
