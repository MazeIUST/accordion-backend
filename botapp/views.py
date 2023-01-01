from django.shortcuts import render
from rest_framework.viewsets import ViewSet
from accounts.models import User
from song.models import Song
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .serializers import *
from rest_framework.permissions import IsAuthenticated


class UserViewSet(ViewSet):
    serializer_class = SignUpSerializer

    def get_permissions(self):
        if self.action == 'signup':
            return [IsAuthenticated()]
        return []

    def start(self, request, chat_id):
        user = get_object_or_404(User, telegram_chat_id=chat_id)
        serializer = UserSerializer(user)
        return Response({'status': 'OK', 'user': serializer.data})

    def login(self, request, chat_id, username, password):
        user = get_object_or_404(User, username=username)
        serializers = LoginSerializer(
            user, data={'chat_id': chat_id, 'username': username, 'password': password})
        serializers.is_valid(raise_exception=True)
        serializers.update(user, serializers.validated_data)

    def signup(self, request, chat_id):
        data = request.data
        data['telegram_chat_id'] = chat_id
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.update(request.user, serializer.validated_data)
        return Response({'status': 'OK'})

    def get_song(self, request, song_id):
        song = get_object_or_404(Song, id=song_id)
        serializer = SongSerializer(song)
        return Response({'status': 'OK', 'song': serializer.data})

    def get_playlists(self, request, chat_id):
        user = get_object_or_404(User, telegram_chat_id=chat_id)
        playlists = Playlist.objects.filter(user=user)
        serializer = PlaylistSerializer(playlists, many=True)
        return Response({'status': 'OK', 'playlists': serializer.data})
