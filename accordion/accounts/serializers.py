from rest_framework import  serializers
from django.contrib.auth.hashers import make_password
from accounts.models import *
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from song.serializers import *

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

class FollowerSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user1.username', read_only=True)
    profile = serializers.HyperlinkedRelatedField(source='user1', read_only=True, view_name='show_other_user_profile')
    
    class Meta:
        model = Follow
        fields = ('username', 'profile')
        
        
class FollowingSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user2.username', read_only=True)
    profile = serializers.HyperlinkedRelatedField(source='user2', read_only=True, view_name='show_other_user_profile')
    
    class Meta:
        model = Follow
        fields = ('username', 'profile')
        
        
class ArtistSerializer(serializers.ModelSerializer):
    songs = serializers.SerializerMethodField()
    class Meta:
        model = Artist
        fields = ['artistic_name', 'activitie_start_date', 'description', 'songs']

    def get_songs(self, obj):
        songs = Song.objects.filter(artist__user=obj.user)
        return SongSerializer(songs, many=True).data


class UserSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer()
    followers_count = serializers.SerializerMethodField()
    followings_count = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()
    followings = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['username', 'is_Artist', 'first_name', 'last_name', 'image', 'followers_count', 'followings_count', 'followers', 'followings', 'artist'] # should add playlist there

        
    def get_followers_count(self, obj):
        followers_count = Follow.objects.filter(user2=obj).count()
        return followers_count
    
    def get_followings_count(self, obj):
        followings_count = Follow.objects.filter(user1=obj).count()
        return followings_count
    
    def get_followers(self, obj):
        followers = Follow.objects.filter(user2=obj)
        return FollowerSerializer(followers, many=True, context={'request': self.context['request']}).data
    
    def get_followings(self, obj):
        followings = Follow.objects.filter(user1=obj)
        return FollowingSerializer(followings, many=True, context={'request': self.context['request']}).data
    


class ArtistPrivateSerializer(ArtistSerializer):
    class Meta(ArtistSerializer.Meta):
        fields = ['id'] + ArtistSerializer.Meta.fields
        read_only_fields = ['id']
        

class UserPrivateSerializer(UserSerializer):
    artist = ArtistPrivateSerializer()
    
    class Meta(UserSerializer.Meta):
        fields = ['id', 'email', 'is_email_verified', 'telegram_chat_id', 'birthday', 'gender', 'country'] + UserSerializer.Meta.fields
        read_only_fields = ['id', 'username', 'is_Artist', 'email', 'is_email_verified', 'telegram_chat_id']      

    def update(self, instance, validated_data):
        try:
            artist_data = validated_data.pop('artist')
            artist = instance.artist
            super().update(artist, artist_data)
        except:
            pass
        return super().update(instance, validated_data)

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
            
