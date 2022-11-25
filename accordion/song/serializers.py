from rest_framework import serializers
from .models import *


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name')

class SongSerializer(serializers.ModelSerializer):

    class Meta:
        model = Song
        fields = ('id', 'artist', 'title', 'description', 'lyrics', 'song_link', 'image', 'note', 'created_at', 'tags')
        read_only_fields = ('id', 'created_at', 'artist')

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        song = Song.objects.create(**validated_data)
        for tag in tags:
            song.tags.add(tag)
        return song

class PlaylistSerializer(serializers.ModelSerializer):

    class Meta:
        model = Playlist
        fields = ('id','title','owner','created_at','is_public','description','image')
        read_only_fields = ('id', 'created_at', 'owner')



        