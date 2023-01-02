from rest_framework import serializers
from .models import *


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name')


class SongSerializer(serializers.ModelSerializer):
    artist_name = serializers.SerializerMethodField()
    song_download_link = serializers.SerializerMethodField()

    class Meta:
        model = Song
        fields = ('id', 'artist', 'artist_name', 'title', 'description', 'lyrics', 'song_link',
                  'speechless_song_link', 'song_download_link', 'image', 'note', 'created_at', 'tags')
        read_only_fields = ('id', 'created_at', 'artist')

    def get_artist_name(self, obj):
        artist = obj.artist
        return artist.artistic_name

    def get_song_download_link(self, obj):
        view_link = obj.song_link
        try:
            song_id = view_link.split('/')[-2]
            song_link = f'https://drive.google.com/u/0/uc?id={song_id}&export=download'
        except:
            song_link = view_link
        return song_link

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        song = Song.objects.create(**validated_data)
        for tag in tags:
            song.tags.add(tag)
        return song


class ProfilePlaylistSerializer(serializers.ModelSerializer):
    link = serializers.HyperlinkedIdentityField(view_name='get_playlist')

    class Meta:
        model = Playlist
        fields = ['id', 'title', 'owner', 'created_at',
                  'is_public', 'description', 'image', 'link']
        read_only_fields = ['id', 'created_at', 'owner', 'link']


class PlaylistSerializer(ProfilePlaylistSerializer):
    songs = serializers.SerializerMethodField()

    class Meta(ProfilePlaylistSerializer.Meta):
        fields = ProfilePlaylistSerializer.Meta.fields + ['songs']
        read_only_fields = ProfilePlaylistSerializer.Meta.read_only_fields + \
            ['songs']

    def get_songs(self, obj):
        playlist_songs = PlaylistSong.objects.filter(playlist=obj)
        songs = [playlist_song.song for playlist_song in playlist_songs]
        return SongSerializer(songs, many=True, context={'request': self.context['request']}).data


class PlaylistSongsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaylistSong
        fields = ('id', 'playlist', 'song')
        read_only_fields = ('id', 'playlist')

    def validate(self, attrs):
        request = self.context.get('request')
        playlist = self.context.get('playlist')
        song = attrs['song']
        if request.method == 'POST':
            if PlaylistSong.objects.filter(playlist=playlist, song=song).exists():
                raise serializers.ValidationError(
                    'Song already exists in playlist')
        elif request.method == 'DELETE':
            if not PlaylistSong.objects.filter(playlist=playlist, song=song).exists():
                raise serializers.ValidationError(
                    'Song does not exist in playlist')
        return attrs


class AlbumSerializer(serializers.ModelSerializer):
    songs = serializers.SerializerMethodField()

    class Meta:
        model = Album
        fields = ('id', 'title', 'artist', 'description', 'image', 'songs')
        read_only_fields = ('id', 'artist')

    def get_songs(self, obj):
        album_songs = AlbumSong.objects.filter(album=obj)
        songs = [album_song.song for album_song in album_songs]
        return SongSerializer(songs, many=True, context={'request': self.context['request']}).data

    def create(self, validated_data):
        user = self.context.get('request').user
        artist = Artist.objects.get(user=user)
        album = Album.objects.create(artist=artist, **validated_data)
        return album


class AlbumSongsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlbumSong
        fields = ('id', 'album', 'song')
        read_only_fields = ('id', 'album')

    def validate(self, attrs):
        request = self.context.get('request')
        album = self.context.get('album')
        song = attrs['song']
        if album.artist != song.artist:
            raise serializers.ValidationError('Song does not belong to artist')
        if request.method == 'POST':
            if AlbumSong.objects.filter(album=album, song=song).exists():
                raise serializers.ValidationError(
                    'Song already exists in album')
        elif request.method == 'DELETE':
            if not AlbumSong.objects.filter(album=album, song=song).exists():
                raise serializers.ValidationError(
                    'Song does not exist in album')
        return attrs


class SongLogsSerializer(serializers.ModelSerializer):
    age = serializers.SerializerMethodField()
    song_details = serializers.SerializerMethodField()

    class Meta:
        model = SongLogs
        fields = ('id', 'user', 'song', 'song_details', 'age', 'created_at')
        read_only_fields = ('id', 'user', 'song_details', 'age', 'created_at')

    def get_age(self, obj):
        user = self.context.get('request').user
        if user.birthday:
            age = datetime.datetime.now().year - user.birthday.year
        else:
            age = None
        return age

    def get_song_details(self, obj):
        song = obj.song
        return SongSerializer(song, context={'request': self.context['request']}).data
