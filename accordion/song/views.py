from rest_framework.viewsets import ViewSet
from .serializers import SongSerializer, TagSerializer,PlaylistSerializer
from rest_framework.response import Response
from accounts.models import Artist
from .models import *
from rest_framework import status
from .scripts import create_tag
from accordion.permissions import *
from django.db.models import Q
from django.shortcuts import get_object_or_404,get_list_or_404
from rest_framework.permissions import IsAuthenticated
       

class SongViewSet(ViewSet):
    serializer_class = SongSerializer

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.action in ['update', 'destroy', 'destroy_all']:
            permission_classes.append(IsArtistORSuperuser)
        elif self.action in ['create']:
            permission_classes.append(IsArtist)
        elif self.action in ['search', 'list']:
            permission_classes = []
        return [permission() for permission in permission_classes]

    def list(self, request):
        # Anonimous users
        if request.user.is_anonymous:
            songs = Song.objects.all()
        elif request.user.is_Artist:
            artist = Artist.objects.get(user=request.user)
            songs = Song.objects.filter(artist=artist)
        else:
            songs = Song.objects.all()
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
        song = get_object_or_404(Song, id=pk)
        serializer = SongSerializer(song)
        return Response(serializer.data)

    def update(self, request, pk=None):
        song = get_object_or_404(Song, id=pk)
        serializer = SongSerializer(instance=song, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk=None):
        song = get_object_or_404(Song, id=pk)
        song.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def destroy_all(self, request):
        if request.user.is_superuser:
            Song.objects.all().delete()
        else:
            artist = Artist.objects.get(user=request.user)
            Song.objects.filter(artist=artist).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def search(self, request, text=None):
        scores = {}
        title_contains = Song.objects.filter(title__contains=text)
        artist_contains = Song.objects.filter(Q(artist__user__first_name__contains=text) | Q(artist__user__last_name__contains=text))
        lyrics_contains = Song.objects.filter(lyrics__contains=text)
        
        for song in title_contains:
            scores[song] = 10
        for song in artist_contains:
            scores[song] = 5 if song not in scores else scores[song] + 5
        for song in lyrics_contains:
            scores[song] = 3 if song not in scores else scores[song] + 3

        # save songs in a queryset
        songs = []
        for song in scores:
            songs.append(song)

        # sort songs by score
        songs.sort(key=lambda x: scores[x], reverse=True)

        # return top 15 songs   
        if len(songs) > 15:
            songs = songs[:15]

        serializer = SongSerializer(songs, many=True)
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
        try:
            tag = Tag.objects.get(id=pk)
            serializer = TagSerializer(tag)
            return Response(serializer.data)
        except Tag.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def update(self, request, pk=None):
        tag = Tag.objects.get(id=pk)
        serializer = TagSerializer(instance=tag, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        try:
            tag = Tag.objects.get(id=pk)
            tag.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Tag.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class PlaylistViewSet(ViewSet):
    serializer_class = PlaylistSerializer
    permission_classes = [IsAuthenticated,IsPlaylistOwner]
        
    # this is working
    def create(self, request):  
        serializer = PlaylistSerializer(data=request.data)
        if serializer.is_valid():
            owner = request.user
            serializer.save(owner=owner)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        playlist = get_object_or_404(Playlist, id=pk)
        playlist.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # this is working
    def retrieve(self, request, pk=None): #return a playlist by its id
        playlist = get_object_or_404(Playlist, id=pk)
        serializer = PlaylistSerializer(playlist)
        return Response(serializer.data)
    
    # this is working
    def retrieve_user_playlists(self, request): # return a playlists of a user for itself
        playlists = get_list_or_404(Playlist, owner_id=request.user.id)
        serializer = PlaylistSerializer(playlists, many=True)
        return Response(serializer.data)

    # this is working
    def retrieve_other_playlists(self, request,pk=None): # return a playlists of a user for itself
        playlists = get_list_or_404(Playlist, owner_id=pk,is_public=True)
        serializer = PlaylistSerializer(playlists,many=True)
        return Response(serializer.data)

    def update(self, request, pk=None):
        playlist = get_object_or_404(Playlist, id=pk)
        serializer = PlaylistSerializer(instance=playlist, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def add_song1(self, request, song_pk=None,playlist_pk=None):
    #     song = get_object_or_404(Song, id=song_pk)
    #     playlist = get_object_or_404(Playlist, id=playlist_pk)
    #     playlist.songs.add(song)
    #     return Response(status=status.HTTP_204_NO_CONTENT)
    

    def add_song(self, request, *args, **kwargs):
        song_pk = self.kwargs.get('song_pk')
        playlist_pk = self.kwargs.get('playlist_pk') 
        song = get_object_or_404(Song, id=song_pk)
        playlist = get_object_or_404(Playlist, id=playlist_pk)
        playlist.songs.add(song)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def remove_song(self, request, song_pk=None,playlist_pk=None):
        song = get_object_or_404(Song, id=song_pk)
        playlist = get_object_or_404(Playlist, id=playlist_pk)
        playlist.songs.delete(song)
        return Response(status=status.HTTP_204_NO_CONTENT)

    





