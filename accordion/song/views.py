from rest_framework.viewsets import ViewSet
from .serializers import SongSerializer, TagSerializer,PlaylistSerializer
from rest_framework.response import Response
from accounts.models import Artist
from .models import *
from rest_framework import status
from .scripts import create_tag
from accordion.permissions import *
from django.db.models import Q,F
from django.shortcuts import get_object_or_404,get_list_or_404
from rest_framework.permissions import IsAuthenticated
from urllib.parse import urlparse, parse_qs

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

    def get_permissions(self):
        permission_classes = [IsAuthenticated, IsPlaylistOwner]
        if self.action in ['get_3_public_playlists']:
            permission_classes = []
        return [permission() for permission in permission_classes]
        
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

    def retrieve(self, request, pk=None):
        playlist = get_object_or_404(Playlist, id=pk)
        serializer = PlaylistSerializer(playlist)
        return Response(serializer.data)
    
    def list(self, request):
        playlists = get_list_or_404(Playlist, owner=request.user)
        serializer = PlaylistSerializer(playlists, many=True)
        return Response(serializer.data)

    def update(self, request, pk=None):
        playlist = get_object_or_404(Playlist, id=pk)
        serializer = PlaylistSerializer(instance=playlist, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def add_song(self, request, pk=None):
        playlist = get_object_or_404(Playlist, id=pk)
        song = get_object_or_404(Song, id=request.data['song'])
        playlist.songs.add(song)
        playlist.save()
        return Response(status=status.HTTP_200_OK)

    def remove_song(self, request, pk=None):
        playlist = get_object_or_404(Playlist, id=pk)
        song = get_object_or_404(Song, id=request.data['song'])
        playlist.songs.remove(song)
        playlist.save()
        return Response(status=status.HTTP_200_OK)

    def get_3_public_playlists(self, request):
        playlists = Playlist.objects.filter(is_public=True)
        if len(playlists) > 3:
            playlists = playlists[:3]
        serializer = PlaylistSerializer(playlists, many=True)
        return Response(serializer.data)
    

class HistoryViewSet(ViewSet):
    def analysis(self, request, days=0, city='0', country='0', min_age=0, max_age=0):
        today = datetime.datetime.now()
        last_time = today-datetime.timedelta(days=days)
        days_filter = Q(add_datetime__range=[last_time,today]) if days!= 0 else Q()
        city_filter = Q(user__city=city) if city!= '0' else Q()
        country_filter = Q(user__country=country) if country!= '0' else Q()
        min_age_filter = Q(user__birthday__lte=today-datetime.timedelta(days=min_age*365)) if min_age!= 0 else Q()
        max_age_filter = Q(user__birthday__gte=today-datetime.timedelta(days=max_age*365)) if max_age!= 0 else Q()
        user_history =History.objects.filter(days_filter,city_filter,country_filter,min_age_filter,max_age_filter)
        songs_tags = user_history.annotate(tags=F("song_id__tags")).values()
        tags = Tag.objects.all()
        result = {}
        for tag in tags:
            result[tag.id]=0
        for song_tag in songs_tags:
            for tag in song_tag.tags:
                result[tag.id]=+1
        return Response(result)


    def analysis2(self, request):
        
        city = self.request.GET.get('city',"0")
        country = self.request.GET.get('country',"0")
        min_age=self.request.GET.get('min_age',"0")
        max_age= self.request.GET.get('max_age',"0")
        days = self.request.GET.get('days','0')

        today = datetime.datetime.now()
        last_time = today-datetime.timedelta(days=int(days))
        days_filter = Q(add_datetime__range=[last_time,today]) if days!= 0 else Q()
        city_filter = Q(user__city=city) if city!= '0' else Q()
        country_filter = Q(user__country=country) if country!= '0' else Q()
        min_age_filter = Q(user__birthday__lte=today-datetime.timedelta(days=min_age*365)) if min_age!= 0 else Q()
        max_age_filter = Q(user__birthday__gte=today-datetime.timedelta(days=max_age*365)) if max_age!= 0 else Q()
        user_history =History.objects.filter(days_filter,city_filter,country_filter,min_age_filter,max_age_filter)
        songs_tags = user_history.annotate(tags=F("song_id__tags")).values()
        tags = Tag.objects.all()
        result = {}
        for tag in tags:
            result[tag.id]=0
        for song_tag in songs_tags:
            for tag in song_tag.tags:
                result[tag.id]=+1
        return Response(result)

    





