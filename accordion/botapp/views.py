from django.shortcuts import render
from rest_framework.viewsets import ViewSet
from accounts.models import User
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .serializers import SignUpSerializer


class UserViewSet(ViewSet):
    serializer_class = SignUpSerializer

    def start(self, request, chat_id):
        user = User.objects.filter(telegram_chat_id=chat_id)
        if user.exists():
            return Response({'status': 'authenticated'})
        else:
            return Response({'status': 'not_authenticated'})

    def signup(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            serializer.update(request.user, request.data)
            return Response({'status': 'OK'})
        return Response({'status': 'error'})

    def get_my_playlists(self, request, chat_id):
        user = User.objects.filter(telegram_chat_id=chat_id)
        if user.exists():
            playlists = user[0].playlists.all()
            playlists = [{'name': playlist.name} for playlist in playlists]
            return Response({'status': 'OK', 'playlists': playlists})