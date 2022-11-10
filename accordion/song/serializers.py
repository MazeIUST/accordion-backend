from rest_framework import serializers
from .models import *


class UploadSongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = ('id', 'artist', 'title', 'description', 'song', 'image', 'note', 'created_at')


    def create(self, validated_data):
        song = Song.objects.create(
            artist=validated_data['artist'],
            title=validated_data['title'],
            description=validated_data['description'],
            song=validated_data['song'],
            image=validated_data['image'],
            note=validated_data['note'],
        )
        return song