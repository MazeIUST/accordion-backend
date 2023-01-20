from rest_framework import serializers
from .models import Song
from django.contrib.sites.shortcuts import get_current_site  # for email
from django.urls import reverse  # for email


class SongSerializer(serializers.ModelSerializer):
    song_link = serializers.SerializerMethodField()

    class Meta:
        model = Song
        fields = ('id', 'file', 'song_link')
        read_only_fields = ('id', 'song_link')

    def get_song_link(self, obj):
        request = self.context.get('request')
        current_site = get_current_site(
            request).domain + '/cloud/download_song/'
        absurl = 'http://' + current_site + str(obj.id)
        return absurl
