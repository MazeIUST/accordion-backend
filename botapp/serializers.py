from rest_framework import serializers
from accounts.models import *
from song.models import *
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import make_password


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'telegram_chat_id')
        read_only_fields = ('id',)


class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'telegram_chat_id')
        read_only_fields = ('id',)

    def update(self, instance, validated_data):
        instance.telegram_chat_id = validated_data.get(
            'telegram_chat_id', instance.telegram_chat_id)
        instance.save()
        return instance


class SongSerializer(serializers.ModelSerializer):
    song_download_link = serializers.SerializerMethodField()
    artist_name = serializers.SerializerMethodField()

    class Meta:
        model = Song
        fields = ('id', 'title', 'song_link',
                  'song_download_link', 'artist_name')

    def get_song_download_link(self, obj):
        view_link = obj.song_link
        try:
            song_id = view_link.split('/')[-2]
            song_link = f'https://drive.google.com/u/0/uc?id={song_id}&export=download'
        except:
            song_link = view_link
        return song_link

    def get_artist_name(self, obj):
        artist = obj.artist
        return artist.artistic_name


class CreateSongSerializer(serializers.ModelSerializer):
    artistic_name = serializers.CharField(write_only=True)

    class Meta:
        model = Song
        fields = ('title', 'image', 'song_link',
                  'telegram_id', 'artistic_name')

    def create(self, validated_data):
        artistic_name = validated_data.pop('artistic_name')
        artist = Artist.objects.filter(artistic_name=artistic_name)
        if artist.exists():
            artist = artist[0]
        else:
            new_user = User.objects.create(
                username=artistic_name, password=make_password('1234'))
            artist = Artist.objects.create(
                user=new_user, artistic_name=artistic_name)
        song = Song.objects.create(artist=artist, **validated_data)
        return song


class PlaylistSerializer(serializers.ModelSerializer):
    songs = serializers.SerializerMethodField()

    class Meta:
        model = Playlist
        fields = ('id', 'title', 'songs')
        read_only_fields = ('id',)

    def get_songs(self, obj):
        playlist_songs = PlaylistSong.objects.filter(playlist=obj)
        songs = [playlist_song.song for playlist_song in playlist_songs]
        return SongSerializer(songs, many=True).data
