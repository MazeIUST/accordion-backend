
from rest_framework import serializers
from .models import *



class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ( 'user_id','song_id')

    def create(self, validated_data):
        history = History.objects.create(
            song_id=validated_data['song_id'],
            user_id=validated_data['user_id'],
        )
        return history