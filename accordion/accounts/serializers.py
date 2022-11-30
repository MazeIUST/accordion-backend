from rest_framework import  serializers
from django.contrib.auth.hashers import make_password
from accounts.models import Artist,User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


# Register serializer
class SignUpSerializer(serializers.ModelSerializer):
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


class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = ('id', 'artistic_name', 'activitie_start_date','description')
        read_only_fields = ('id',)


class UserSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer()
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'is_email_verified', 'is_Artist', 'telegram_chat_id', 'first_name','last_name', 'birthday', 'gender', 'country', 'image', 'artist')
        read_only_fields = ('id', 'email', 'username', 'is_email_verified', 'is_Artist', 'telegram_chat_id')
        

    def update(self, instance, validated_data):
        try:
            artist_data = validated_data.pop('artist')
            artist = instance.artist
            super().update(artist, artist_data)
        except:
            pass
        return super().update(instance, validated_data)

class ArtistPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = ( 'artistic_name', 'activitie_start_date','description') # should add songs 
        read_only_fields = ( 'artistic_name', 'activitie_start_date','description') # should add songs 

class UserPublicSerializer(serializers.ModelSerializer):
    artist = ArtistPublicSerializer()
    class Meta:
        model = User
        fields = ('username', 'is_Artist', 'first_name','last_name', 'image', 'artist','following') # should add playlist, followings there
        read_only_fields = ('username', 'is_Artist', 'first_name','last_name', 'image', 'artist','following') # should add playlist,followings there



class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        is_email_verified = self.user.is_email_verified
        if not is_email_verified and not self.user.is_superuser:
            raise serializers.ValidationError({
                'email': ['email is not verified.'],
            })

        return data

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password1 = serializers.CharField(required=True)
    new_password2 = serializers.CharField(required=True)
    class Meta:
        model = User
        fields = ('old_password', 'new_password1', 'new_password2')

    def validate(self, attrs):
        if attrs['new_password1'] != attrs['new_password2']:
            raise serializers.ValidationError({
                'new_password2': ['Passwords must match.'],
            })
        if attrs['old_password'] == attrs['new_password1']:
            raise serializers.ValidationError({
                'new_password1': ['New password must be different than old password.'],
            })
        return attrs

    def update(self, instance, validated_data):
        if instance.check_password(validated_data['old_password']):
            instance.set_password(validated_data['new_password1'])
            instance.save()
            return instance
        else:
            raise serializers.ValidationError({
                'old_password': ['Old password is incorrect.'],
            })
            
