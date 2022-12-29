from rest_framework.viewsets import ViewSet, ModelViewSet
from .serializers import *
from rest_framework.response import Response
from accounts.models import Artist
from .models import *
from rest_framework import status
from .scripts import create_tag
from accordion.permissions import *
from django.db.models import Q , F
from django.shortcuts import get_object_or_404, get_list_or_404
from rest_framework.permissions import IsAuthenticated


class SongViewSet(ViewSet):
    serializer_class = SongSerializer

    def get_permissions(self):
        permission_classes = []
        if self.action in ['update', 'destroy', 'destroy_all']:
            permission_classes = [IsAuthenticated, IsArtistORSuperuser]
        elif self.action in ['create']:
            permission_classes = [IsAuthenticated, IsArtist]
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
        serializer = SongSerializer(
            songs, many=True, context={'request': request})
        return Response(serializer.data)

    def create(self, request):
        artist = Artist.objects.get(user=request.user)
        serializer = SongSerializer(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(artist=artist)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        song = get_object_or_404(Song, id=pk)
        serializer = SongSerializer(song, context={'request': request})
        return Response(serializer.data)

    def update(self, request, pk=None):
        song = get_object_or_404(Song, id=pk)
        serializer = SongSerializer(
            instance=song, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

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
        artist_contains = Song.objects.filter(
            Q(artist__user__first_name__contains=text) | Q(artist__user__last_name__contains=text))
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

        serializer = SongSerializer(
            songs, many=True, context={'request': request})
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
        serializer = TagSerializer(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        tag = get_object_or_404(Tag, id=pk)
        serializer = TagSerializer(tag, context={'request': request})
        return Response(serializer.data)

    def update(self, request, pk=None):
        tag = Tag.objects.get(id=pk)
        serializer = TagSerializer(
            instance=tag, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        tag = get_object_or_404(Tag, id=pk)
        tag.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PlaylistViewSet(ModelViewSet):
    queryset = Playlist.objects.all()

    def get_permissions(self):
        permission_classes = [IsAuthenticated, IsPlaylistOwner]
        if self.action in ['get_3_public_playlists']:
            permission_classes = []
        elif self.action in ['retrieve']:
            permission_classes = [IsAuthenticated, IsPublicPlaylist]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action in ['add_song', 'remove_song']:
            return PlaylistSongsSerializer
        return PlaylistSerializer

    def create(self, request):
        owner = request.user
        serializer = PlaylistSerializer(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=owner)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None):
        playlist = get_object_or_404(Playlist, id=pk)
        playlist.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def retrieve(self, request, pk=None):
        playlist = get_object_or_404(Playlist, pk=pk)
        serializer = PlaylistSerializer(playlist, context={'request': request})
        return Response(serializer.data)

    def list(self, request):
        playlists = get_list_or_404(Playlist, owner=request.user)
        serializer = PlaylistSerializer(
            playlists, many=True, context={'request': request})
        return Response(serializer.data)

    def update(self, request, pk=None):
        playlist = get_object_or_404(Playlist, pk=pk)
        serializer = PlaylistSerializer(
            instance=playlist, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def add_song(self, request, pk=None):
        playlist = get_object_or_404(Playlist, pk=pk)
        song = get_object_or_404(Song, pk=request.data['song'])
        serializer = PlaylistSongsSerializer(data=request.data, context={
                                             'request': request, 'playlist': playlist})
        serializer.is_valid(raise_exception=True)
        serializer.save(playlist=playlist, song=song)
        return Response({'message': 'Song added to playlist'}, status=status.HTTP_200_OK)

    def remove_song(self, request, playlist_pk=None, song_pk=None):
        playlist = get_object_or_404(Playlist, pk=playlist_pk)
        song = get_object_or_404(Song, pk=song_pk)
        playlistsong = get_object_or_404(
            PlaylistSong, playlist=playlist, song=song)
        playlistsong.delete()
        return Response({'message': 'Song removed from playlist'}, status=status.HTTP_200_OK)

    def get_3_public_playlists(self, request):
        playlists = Playlist.objects.filter(is_public=True)
        if len(playlists) > 3:
            playlists = playlists[:3]
        serializer = PlaylistSerializer(
            playlists, many=True, context={'request': request})
        return Response(serializer.data)


class AlbumViewSet(ModelViewSet):
    queryset = Album.objects.all()

    def get_serializer_class(self):
        if self.action in ['add_song', 'remove_song']:
            return AlbumSongsSerializer
        return AlbumSerializer

    def get_permissions(self):
        if self.action in ['retrieve']:
            permission_classes = []
        elif self.action in ['update', 'destroy', 'add_song', 'remove_song']:
            permission_classes = [IsAuthenticated, IsAlbumOwner]
        else:
            permission_classes = [IsAuthenticated, IsArtist]
        return [permission() for permission in permission_classes]

    def create(self, request):
        serializer = AlbumSerializer(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None):
        album = get_object_or_404(Album, id=pk)
        album.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def retrieve(self, request, pk=None):
        album = get_object_or_404(Album, id=pk)
        serializer = AlbumSerializer(album, context={'request': request})
        return Response(serializer.data)

    def update(self, request, pk=None):
        album = get_object_or_404(Album, id=pk)
        serializer = AlbumSerializer(
            instance=album, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request):
        albums = Album.objects.all().filter(artist__user=request.user)
        serializer = AlbumSerializer(
            albums, many=True, context={'request': request})
        return Response(serializer.data)

    def add_song(self, request, pk=None):
        album = get_object_or_404(Album, pk=pk)
        song = get_object_or_404(Song, pk=request.data['song'])
        serializer = AlbumSongsSerializer(data=request.data, context={
            'request': request, 'album': album})
        serializer.is_valid(raise_exception=True)
        serializer.save(album=album, song=song)
        return Response({'message': 'Song added to album'}, status=status.HTTP_200_OK)

    def remove_song(self, request, album_pk=None, song_pk=None):
        album = get_object_or_404(Album, pk=album_pk)
        song = get_object_or_404(Song, pk=song_pk)
        albumsong = get_object_or_404(
            AlbumSong, album=album, song=song)
        albumsong.delete()


class HistoryViewSet(ViewSet):
    serializer_class = HistorySerializer

    def create(self, request):
        serializer = HistorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def analysis_tags(self, request, days=0, city='0', country='0', min_age=0, max_age=0):
        today = datetime.datetime.now()
        last_time = today-datetime.timedelta(days=days)
        days_filter = Q(add_datetime__range=[
                        last_time, today]) if days != 0 else Q()
        city_filter = Q(user__city=city) if city != '0' else Q()
        country_filter = Q(user__country=country) if country != '0' else Q()
        min_age_filter = Q(user__birthday__lte=today -
                           datetime.timedelta(days=min_age*365)) if min_age != 0 else Q()
        max_age_filter = Q(user__birthday__gte=today -
                           datetime.timedelta(days=max_age*365)) if max_age != 0 else Q()
        user_history = History.objects.filter(
            days_filter, city_filter, country_filter, min_age_filter, max_age_filter)
        songs_tags = user_history.annotate(tags=F("song_id__tags")).values()
        tags = Tag.objects.all()
        result = {}
        for tag in tags:
            result[tag.id] = 0
        for song_tag in songs_tags:
            for tag in song_tag.tags:
                result[tag.id] = +1
        return Response(result)

    def analysis_artists(self, request, days=0, city='0', country='0', min_age=0, max_age=0):
        today = datetime.datetime.now()
        last_time = today-datetime.timedelta(days=days)
        days_filter = Q(add_datetime__range=[
                        last_time, today]) if days != 0 else Q()
        city_filter = Q(user__city=city) if city != '0' else Q()
        country_filter = Q(user__country=country) if country != '0' else Q()
        min_age_filter = Q(user__birthday__lte=today -
                           datetime.timedelta(days=min_age*365)) if min_age != 0 else Q()
        max_age_filter = Q(user__birthday__gte=today -
                           datetime.timedelta(days=max_age*365)) if max_age != 0 else Q()
        user_history = History.objects.filter(
            days_filter, city_filter, country_filter, min_age_filter, max_age_filter)
        songs_artist = []
        for item in user_history:
            songs_artist.append(item.song.artist)
        result ={i:songs_artist.count(i) for i in songs_artist}
        
        return Response(result)

    # def analysis2(self, request):
    #     city = self.request.GET.get('city', "0")
    #     country = self.request.GET.get('country', "0")
    #     min_age = self.request.GET.get('min_age', "0")
    #     max_age = self.request.GET.get('max_age', "0")
    #     days = self.request.GET.get('days', '0')

    #     today = datetime.datetime.now()
    #     last_time = today-datetime.timedelta(days=int(days))
    #     days_filter = Q(add_datetime__range=[
    #                     last_time, today]) if days != 0 else Q()
    #     city_filter = Q(user__city=city) if city != '0' else Q()
    #     country_filter = Q(user__country=country) if country != '0' else Q()
    #     min_age_filter = Q(user__birthday__lte=today -
    #                        datetime.timedelta(days=min_age*365)) if min_age != 0 else Q()
    #     max_age_filter = Q(user__birthday__gte=today -
    #                        datetime.timedelta(days=max_age*365)) if max_age != 0 else Q()
    #     user_history = History.objects.filter(
    #         days_filter, city_filter, country_filter, min_age_filter, max_age_filter)
    #     songs_tags = user_history.annotate(tags=F("song_id__tags")).values()
    #     tags = Tag.objects.all()
    #     result = {}
    #     for tag in tags:
    #         result[tag.id] = 0
    #     for song_tag in songs_tags:
    #         for tag in song_tag.tags:
    #             result[tag.id] = +1
    #     return Response(result)
