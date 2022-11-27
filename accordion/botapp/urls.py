from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import *


urlpatterns = [
    path('signup/', UserViewSet.as_view({'put': 'signup'})),
    path('start/<int:chat_id>/', UserViewSet.as_view({'get': 'start'})),
    path('get_my_playlists/<int:chat_id>/', UserViewSet.as_view({'get': 'get_my_playlists'})),
]