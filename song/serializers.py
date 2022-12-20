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
        fields = ('id', 'artist', 'artist_name', 'title', 'description', 'lyrics',
                  'song_link', 'song_download_link', 'image', 'note', 'created_at', 'tags')
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
