from rest_framework import serializers
from accounts.models import *
from song.models import *
from django.shortcuts import get_object_or_404


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


class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password')
        read_only_fields = ('id',)

    def validate(self, data):
        user = get_object_or_404(User, username=data['username'])
        if user.check_password(data['password']):
            return user
        else:
            raise serializers.ValidationError({'password': 'Wrong password'})

    def update(self, instance, validated_data):
        instance.telegram_chat_id = validated_data.get(
            'chat_id', instance.telegram_chat_id)
        instance.save()
        return instance


class SongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = ('id', 'title', 'song_link', 'song_download_link', 'artist__name')


class PlaylistSerializer(serializers.ModelSerializer):
    songs = serializers.SerializerMethodField()
    class Meta:
        model = Playlist
        fields = ('id', 'name', 'songs')
        read_only_fields = ('id',)
        
    def get_songs(self, obj):
        playlist_songs = PlaylistSong.objects.filter(playlist=obj)
        songs = [playlist_song.song for playlist_song in playlist_songs]
        return SongSerializer(songs, many=True, context={'request': self.context['request']}).data
