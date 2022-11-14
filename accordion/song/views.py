from rest_framework.viewsets import ViewSet
from .serializers import SongSerializer, TagSerializer
from rest_framework.response import Response
from accounts.models import Artist
from .models import *
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from .scripts import create_tag


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
            serializer.save(artist=artist)
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


class ZahraViewSet(ViewSet):
    serializer_class = SongSerializer
    authentication_classes = []
    permission_classes = []

    def create(self, request):
        serializer = SongSerializer(data=request.data)
        if serializer.is_valid():
            artist = Artist.objects.get(user__id = 2)
            serializer.save(artist=artist)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)        


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


class TagViewSet(ViewSet):
    serializer_class = TagSerializer
    authentication_classes = []
    permission_classes = []

    def list(self, request):
        create_tag()
        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = TagSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        tag = Tag.objects.get(id=pk)
        serializer = TagSerializer(tag)
        return Response(serializer.data)

    def update(self, request, pk=None):
        tag = Tag.objects.get(id=pk)
        serializer = TagSerializer(instance=tag, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        tag = Tag.objects.get(id=pk)
        tag.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)