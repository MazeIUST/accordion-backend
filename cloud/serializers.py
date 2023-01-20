from rest_framework import serializers
from .models import Song


class SongSerializer(serializers.Serializer):
    class Meta:
        model = Song
        fields = ('id', 'file')
        read_only_fields = ('id',)
