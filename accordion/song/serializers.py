from rest_framework import serializers
from .models import *



class SongSerializer(serializers.ModelSerializer):

    class Meta:
        model = Song
        fields = ('id', 'artist', 'title', 'description', 'song_link', 'image', 'note', 'created_at')
        read_only_fields = ('id', 'created_at', 'artist')
