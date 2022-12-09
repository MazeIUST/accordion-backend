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
        fields = ('id', 'artist', 'artist_name', 'title', 'description', 'lyrics', 'song_link', 'song_download_link', 'image', 'note', 'created_at', 'tags')
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


class PlaylistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playlist
        fields = ('id', 'title', 'owner', 'created_at', 'is_public', 'description', 'image', 'songs')
        read_only_fields = ('id', 'created_at', 'owner')   

    def create(self, validated_data):
        songs = validated_data.pop('songs')
        playlist = Playlist.objects.create(**validated_data)
        for song in songs:
            playlist.songs.add(song)
        return playlist     