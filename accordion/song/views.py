from rest_framework.viewsets import ViewSet
from .serializers import SongSerializer
from rest_framework.response import Response
from accounts.models import Artist
from .models import Song
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication, SessionAuthentication

class SongView(APIView):
    serializer_class = SongSerializer
    
    def put(self, request, *args, **kwargs):
        serializer = SongSerializer(data=request.data)
        if serializer.is_valid():
            artist = Artist.objects.get(user=request.user)
            serializer.save(artist=artist, current_site=request.get_host())
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        song_id = kwargs.get('song_id')
        if song_id:
            song = Song.objects.get(id=song_id)
            serializer = SongSerializer(song)
            return Response(serializer.data)
        else:
            artist = Artist.objects.get(user=request.user)
            songs = Song.objects.filter(artist=artist)
            serializer = SongSerializer(songs, many=True)
            return Response(serializer.data)

