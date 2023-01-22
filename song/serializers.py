from rest_framework import serializers
from .models import *


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name')


class SongSerializer(serializers.ModelSerializer):
    artist_name = serializers.SerializerMethodField()
    song_download_link = serializers.SerializerMethodField()
    count = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)
    show_tags = serializers.SerializerMethodField()
    tags = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Song
        fields = ('id', 'artist', 'artist_name', 'title', 'description', 'lyrics', 'song_link',
                  'speechless_song_link', 'song_download_link', 'image', 'note', 'created_at', 'count', 'tags', 'show_tags')
        read_only_fields = ('id', 'created_at', 'artist', 'show_tags')

    def validate(self, attrs):
        tags = attrs.get('tags').split(',')
        # check is integer
        for tag in tags:
            try:
                int(tag)
            except:
                raise serializers.ValidationError(
                    f'{tag} is not integer')
        tags = map(int, tags)
        for tag in tags:
            if not Tag.objects.filter(id=tag).exists():
                raise serializers.ValidationError(
                    f'Tag with id: {tag} does not exist')
        return attrs

    def get_artist_name(self, obj):
        artist = obj.artist
        return artist.artistic_name

    def get_song_download_link(self, obj):
        view_link = obj.song_link
        try:
            if 'google' in view_link:
                song_id = view_link.split('/')[-2]
                song_link = f'https://drive.google.com/u/0/uc?id={song_id}&export=download'
            else:
                song_link = view_link
        except:
            song_link = view_link
        return song_link

    def get_count(self, obj):
        logs_count = SongLogs.objects.filter(song=obj).count()
        return logs_count

    def get_show_tags(self, obj):
        tags = obj.tags.all()
        return TagSerializer(tags, many=True).data

    def create(self, validated_data):
        tags = map(int, validated_data.pop('tags').split(','))
        tags = Tag.objects.filter(id__in=tags)
        song = super().create(validated_data)
        song.tags.set(tags)
        return song

    def update(self, instance, validated_data):
        tags = map(int, validated_data.pop('tags').split(','))
        tags = Tag.objects.filter(id__in=tags)
        song = super().update(instance, validated_data)
        song.tags.set(tags)
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


class TagAnalysisSerializer(serializers.ModelSerializer):
    percent = serializers.SerializerMethodField()
    count = serializers.SerializerMethodField()

    class Meta:
        model = Tag
        fields = ('id', 'name', 'count', 'percent')

    def get_count(self, obj):
        tags = self.context.get('tags')
        for tag in tags:
            if tag['song__tags'] == obj.id:
                return tag['count']
        return 0

    def get_percent(self, obj):
        return 0


class ArtistAnalysisSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    percent = serializers.SerializerMethodField()
    count = serializers.SerializerMethodField()

    class Meta:
        model = Artist
        fields = ('id', 'name', 'count', 'percent')

    def get_name(self, obj):
        artistic_name = obj.artistic_name
        first_name = obj.user.first_name
        last_name = obj.user.last_name
        username = obj.user.username
        return artistic_name if artistic_name else f'{first_name} {last_name}' if first_name and last_name else username

    def get_count(self, obj):
        artists = self.context.get('artists')
        for artist in artists:
            if artist['song__artist'] == obj.id:
                return artist['count']
        return 0

    def get_percent(self, obj):
        return 0


class SongAnalysisSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    percent = serializers.SerializerMethodField()
    count = serializers.SerializerMethodField()

    class Meta:
        model = Song
        fields = ('id', 'name', 'count', 'percent')

    def get_name(self, obj):
        return obj.title

    def get_count(self, obj):
        songs = self.context.get('songs')
        for song in songs:
            if song['song'] == obj.id:
                return song['count']
        return 0

    def get_percent(self, obj):
        return 0
