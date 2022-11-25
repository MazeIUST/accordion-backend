from rest_framework import  serializers
from django.contrib.auth.hashers import make_password
from accounts.models import Artist,User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


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
        fields = ('id', 'username', 'email', 'is_email_verified', 'is_Artist','first_name','last_name', 'birthday','gender', 'country')


class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = ('id', 'artistic_name', 'activitie_start_date','description')
        read_only_fields = ('id',)


class ProfileSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer()
    class Meta:
        model = User
        fields = ('id','username', 'first_name','last_name', 'birthday', 'country','city','bio','gender','image_url','email', 'artist')
        read_only_fields = ('id', 'email', 'username')
        

    def update(self, instance, validated_data):
        artist_data = validated_data.pop('artist')
        artist = instance.artist
        super().update(artist, artist_data)
        return super().update(instance, validated_data)

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        is_email_verified = self.user.is_email_verified
        if not is_email_verified:
            raise serializers.ValidationError({
                'email': ['email is not verified.'],
            })

        return data