from rest_framework import serializers
from accounts.models import *


class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'telegram_chat_id')
        read_only_fields = ('id',)


    def update(self, instance, validated_data):
        instance.telegram_chat_id = validated_data.get('telegram_chat_id', instance.telegram_chat_id)
        instance.save()
        return instance

        