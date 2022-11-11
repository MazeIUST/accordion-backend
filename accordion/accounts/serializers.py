from rest_framework import  serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions  import  AuthenticationFailed
from django.db import models
# from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from rest_framework.authtoken.serializers import AuthTokenSerializer
from accounts.models import Artist,User
from rest_framework.response import Response
from rest_framework.authtoken.serializers import AuthTokenSerializer
from django.contrib.auth import login
# Register serializer
class RegisterSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    is_Artist = serializers.BooleanField(required=False)
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password1', 'password2', 'is_Artist')
        extra_kwargs = {
            'password1': {'write_only': True},
            'password1': {'write_only': True},
        }

    def validate(self, attrs):
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError({
                'password2': ['Passwords must match.'],
            })
        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            is_Artist=validated_data['is_Artist'],
            password=make_password(validated_data['password1'])
        )
        if validated_data['is_Artist']:
            Artist.objects.create(user=user)

        return user

# User serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'is_email_verified', 'is_Artist','name', 'birthday','gender', 'country','password')

class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255,min_length=3)
    password = serializers.CharField(max_length=255,min_length=3,write_only=True)
    username = serializers.CharField(max_length=100 ,read_only=True)
    tokens = serializers.CharField(max_length=60,min_length=3,read_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password','tokens')

    def validate(self,attrs):
        email = attrs.get('email','')
        password = attrs.get('password','')
        # user= authenticate(email=email,password=password)
        # query = User.objects.filter(email=email,password=password)
        # if not query:
        #     raise AuthenticationFailed("Invalid credentials, try again")
        # user = query[0]
        # if not user.is_email_verified:
        #     raise AuthenticationFailed("Email is not verified")
        
        # return {
        #     'email': user.email,
        #     'username': user.username,
        #     'tokens': user.tokens

        # }
        pass