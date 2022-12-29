from django.shortcuts import render
from rest_framework.viewsets import ViewSet
from accounts.models import User
from song.models import Song
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .serializers import SignUpSerializer
from rest_framework.permissions import IsAuthenticated



class UserViewSet(ViewSet):
    serializer_class = SignUpSerializer
    
    def get_permissions(self):
        if self.action == 'signup':
            return [IsAuthenticated()]
        return []
    

    def start(self, request, chat_id):
        user = User.objects.filter(telegram_chat_id=chat_id)
        if user.exists():
            return Response({'status': 'authenticated'})
        else:
            return Response({'status': 'not_authenticated'})

    def signup(self, request, chat_id):
        data = request.data 
        data['telegram_chat_id'] = chat_id
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.update(request.user, serializer.validated_data)
        return Response({'status': 'OK'})
        
    def get_song(self, request, song_id):
        song = get_object_or_404(Song, id=song_id)
        return Response({'status': 'OK', 'song': song.song_link})

        