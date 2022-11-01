from rest_framework import serializers
from .models import User

# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

# Register Serializer
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        user_with_same_email = User.objects.all().filter(email=validated_data['email'])
        if user_with_same_email:
            raise serializers.ValidationError({'email': 'Email already exists'})
        user = User.objects.create_user(validated_data['username'], validated_data['email'], validated_data['password'])

        return user