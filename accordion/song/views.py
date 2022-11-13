from rest_framework.viewsets import ViewSet
from .serializers import SongSerializer
from rest_framework.response import Response
from accounts.models import Artist
from .models import Song
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication, SessionAuthentication


class SongViewSet_Artist(ViewSet):
    serializer_class = SongSerializer

    def list(self, request):
        artist = Artist.objects.get(user=request.user)
        songs = Song.objects.filter(artist=artist)
        serializer = SongSerializer(songs, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = SongSerializer(data=request.data)
        if serializer.is_valid():
            artist = Artist.objects.get(user=request.user)
            serializer.save(artist=artist, current_site=request.get_host())
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        song = Song.objects.get(id=pk)
        serializer = SongSerializer(song)
        return Response(serializer.data)

    def update(self, request, pk=None):
        song = Song.objects.get(id=pk)
        serializer = SongSerializer(instance=song, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        song = Song.objects.get(id=pk)
        song.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SongViewSet_User(ViewSet):
    serializer_class = SongSerializer
    authentication_classes = []
    permission_classes = []

    def list(self, request):
        songs = Song.objects.all()
        if len(songs) > 15:
            songs = songs[:15]
    
        serializer = SongSerializer(songs, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        song = Song.objects.get(id=pk)
        serializer = SongSerializer(song)
        return Response(serializer.data)