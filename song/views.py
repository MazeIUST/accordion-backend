from rest_framework.viewsets import ViewSet, ModelViewSet
from .serializers import *
from rest_framework.response import Response
from accounts.models import Artist
from .models import *
from rest_framework import status
from .scripts import create_tag
from accordion.permissions import *
from django.db.models import Q, F
from django.shortcuts import get_object_or_404, get_list_or_404
from rest_framework.permissions import IsAuthenticated
from urllib.parse import urlparse, parse_qs
from django.conf import settings
import requests
from django.db.models import Count


class SongViewSet(ViewSet):
    serializer_class = SongSerializer

    def get_permissions(self):
        permission_classes = []
        if self.action in ['update', 'destroy', 'destroy_all']:
            permission_classes = [IsAuthenticated, IsArtistORSuperuser]
        elif self.action in ['create']:
            permission_classes = [IsAuthenticated, IsArtist]
        elif self.action in ['send_to_telegram']:
            permission_classes = [IsAuthenticated]
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
        title_contains = Song.objects.filter(title__icontains=text)
        artist_contains = Song.objects.filter(
            Q(artist__user__first_name__icontains=text) | Q(artist__user__last_name__icontains=text) | Q(artist__artistic_name__icontains=text))
        lyrics_contains = Song.objects.filter(lyrics__icontains=text)

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

    def top_5_artist_song(self, request, pk=None):
        artist = get_object_or_404(Artist, id=pk) if pk else get_object_or_404(
            Artist, user=request.user)
        topsongs = Song.objects.filter(artist=artist).order_by("-count")[:5]
        result = []
        for song in topsongs:
            p = Point(X=song.title, Y=song.count)
            result.append(p.__dict__)
        return Response(result)

    def send_to_telegram(self, request, pk=None):
        song = get_object_or_404(Song, id=pk)
        user = request.user
        chat_id = user.telegram_chat_id
        serializer = SongSerializer(song, context={'request': request})
        song_link = serializer.data['song_download_link']
        if not chat_id:
            return Response({'message': 'You have to connect your telegram account first'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # send song to telegram
            link = f'https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendAudio?chat_id={chat_id}&audio={song_link}'
            response = requests.get(link)
            if response.status_code == 200:
                return Response({'message': 'Song sent to telegram'}, status=status.HTTP_200_OK)
            return Response({'message': 'Something went wrong'}, status=status.HTTP_400_BAD_REQUEST)


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


class Point():
    def __init__(self, X, Y):
        self.x = X
        self.y = Y


class SongLogsViewSet(ViewSet):
    serializer_class = SongLogsSerializer

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.action in ['analysis', 'convert_to_percents']:
            permission_classes = []
        return [permission() for permission in permission_classes]

    def create(self, request):
        serializer = SongLogsSerializer(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request):
        history = SongLogs.objects.filter(user=request.user)
        serializer = SongLogsSerializer(
            history, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve_by_song(self, request, song_pk=None):
        song = get_object_or_404(Song, pk=song_pk)
        history = SongLogs.objects.filter(user=request.user, song=song)
        serializer = SongLogsSerializer(
            history, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve_by_artist(self, request, artist_pk=None):
        artist = get_object_or_404(Artist, pk=artist_pk)
        history = SongLogs.objects.filter(
            user=request.user, song__artist=artist)
        serializer = SongLogsSerializer(
            history, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve_by_user(self, request, user_pk=None):
        user = get_object_or_404(User, pk=user_pk)
        history = SongLogs.objects.filter(user=user)
        serializer = SongLogsSerializer(
            history, many=True, context={'request': request})
        return Response(serializer.data)

    def make_filters(self, days=0, city='0', min_age=0, max_age=0, user=None, artist=None):
        today = datetime.datetime.now()
        last_time = today-datetime.timedelta(days=days)
        days_filter = Q(created_at__range=[
                        last_time, today]) if days != 0 else Q()
        city_filter = Q(user__city=city) if city != '0' else Q()
        min_age_filter = Q(user__birthday__lte=today -
                           datetime.timedelta(days=min_age*365)) if min_age != 0 else Q()
        max_age_filter = Q(user__birthday__gte=today -
                           datetime.timedelta(days=max_age*365)) if max_age != 0 else Q()
        user_filter = Q(user=user) if user != None else Q()
        artist_filter = Q(song__artist=artist) if artist != None else Q()
        annotate_on_songs = SongLogs.objects.filter(days_filter & city_filter & min_age_filter &
                                                    max_age_filter & user_filter & artist_filter).values('song').annotate(count=Count('song'))
        annotate_on_tags = SongLogs.objects.filter(days_filter & city_filter & min_age_filter & max_age_filter & user_filter & artist_filter).values(
            'song__tags').annotate(count=Count('song__tags'))
        annotate_on_artists = SongLogs.objects.filter(days_filter & city_filter & min_age_filter & max_age_filter & user_filter & artist_filter).values(
            'song__artist').annotate(count=Count('song__artist'))
        result = {'songs': annotate_on_songs,
                  'tags': annotate_on_tags, 'artists': annotate_on_artists}
        return result

    def convert_to_percents(self, data, sort_by_id=False, top5=False):
        # remove 0 count
        data = [d for d in data if d['count'] > 0]
        if sort_by_id:
            data = sorted(data, key=lambda k: k['id'], reverse=True)
        else:
            data = sorted(data, key=lambda k: k['count'], reverse=True)
        if top5:
            data = data[:5] if len(data) > 5 else data

        new_data = []
        total = sum([d['count'] for d in data])
        if total == 0:
            return new_data
        for tag in data:
            tag['percent'] = round(tag['count']*100/total, 2)
            new_data.append(tag)
        new_data = sorted(new_data, key=lambda k: k['count'], reverse=True)
        return new_data

    def analysis(self, request, days=0, city='0', min_age=0, max_age=0, user=None, artist=None, model=None, serializer=None, sort_by_id=False, top5=False):
        logs = self.make_filters(days, city, min_age, max_age, user, artist)
        queryset = model.objects.all()
        serializers = serializer(queryset, many=True, context={
                                 'request': request, 'songs': logs['songs'], 'tags': logs['tags'], 'artists': logs['artists']})
        data = serializers.data
        data = self.convert_to_percents(data, sort_by_id, top5)
        return data

    def analysis_all(self, request, days=0, city='0', min_age=0, max_age=0):
        by_tags = self.analysis(
            request, days, city, min_age, max_age, None, None, Tag, TagAnalysisSerializer)
        by_artists = self.analysis(
            request, days, city, min_age, max_age, None, None, Artist, ArtistAnalysisSerializer)

        results = {'by_tags': by_tags, 'by_artists': by_artists}

        return Response(results)

    def analysis_for_user(self, request, days=0):
        user = request.user
        by_tags = self.analysis(
            request, days=days, user=user, model=Tag, serializer=TagAnalysisSerializer)
        by_artists = self.analysis(
            request, days=days, user=user, model=Artist, serializer=ArtistAnalysisSerializer)
        by_top_songs = None
        by_last_songs = None
        artist = Artist.objects.filter(user=user).first()
        if artist:
            by_top_songs = self.analysis(
                request, days=days, user=user, artist=artist, model=Song, serializer=SongAnalysisSerializer, top5=True)
            by_last_songs = self.analysis(
                request, days=days, user=user, artist=artist, model=Song, serializer=SongAnalysisSerializer, sort_by_id=True, top5=True)

        results = {
            'by_tags': by_tags,
            'by_artists': by_artists,
            'by_top_songs': by_top_songs,
            'by_last_songs': by_last_songs,
            'status': 'OK',
        }

        return Response(results)
