from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from accounts.models import *
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from song.serializers import *
from datetime import datetime, timedelta

# Register serializer


class SignUpSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    is_Artist = serializers.BooleanField(required=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'email',
                  'password1', 'password2', 'is_Artist')
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
    id = serializers.IntegerField(source='user1.id', read_only=True)
    username = serializers.CharField(source='user1.username', read_only=True)
    profile = serializers.HyperlinkedRelatedField(
        source='user1', read_only=True, view_name='show_other_user_profile')
    image = serializers.ImageField(source='user1.image', read_only=True)

    class Meta:
        model = Follow
        fields = ('id', 'username', 'profile', 'image')


class FollowingSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='user2.id', read_only=True)
    username = serializers.CharField(source='user2.username', read_only=True)
    profile = serializers.HyperlinkedRelatedField(
        source='user2', read_only=True, view_name='show_other_user_profile')
    image = serializers.ImageField(source='user2.image', read_only=True)

    class Meta:
        model = Follow
        fields = ('id', 'username', 'profile', 'image')


class ArtistSerializer(serializers.ModelSerializer):
    songs = serializers.SerializerMethodField()
    albums = serializers.SerializerMethodField()

    class Meta:
        model = Artist
        fields = ['artistic_name', 'activitie_start_date',
                  'description', 'songs', 'albums']

    def get_songs(self, obj):
        songs = Song.objects.filter(artist__user=obj.user)
        return SongSerializer(songs, many=True, context={'request': self.context['request']}).data
    
    def get_albums(self, obj):
        albums = Album.objects.filter(artist__user=obj.user)
        return AlbumSerializer(albums, many=True, context={'request': self.context['request']}).data


class UserSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer()
    followers_count = serializers.SerializerMethodField()
    followings_count = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()
    followings = serializers.SerializerMethodField()
    playlists = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'is_Artist', 'first_name', 'last_name', 'image', 'bio', 'followers_count',
                  'followings_count', 'followers', 'followings', 'artist', 'playlists']  # should add playlist there
        read_only_fields = ['id', 'username', 'email', 'playlists']

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

    def get_playlists(self, obj):
        playlists = Playlist.objects.filter(owner=obj, is_public=True)
        return ProfilePlaylistSerializer(playlists, many=True, context={'request': self.context['request']}).data


class ArtistPrivateSerializer(ArtistSerializer):
    class Meta(ArtistSerializer.Meta):
        fields = ['id'] + ArtistSerializer.Meta.fields
        read_only_fields = ['id']


class UserPrivateSerializer(UserSerializer):
    artist = ArtistPrivateSerializer()
    premium = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = ['email', 'is_email_verified', 'telegram_chat_id', 'birthday',
                                               'gender', 'country', 'city', 'bio', 'money', 'premium'] + UserSerializer.Meta.fields
        read_only_fields = ['id', 'username', 'is_Artist', 'email',
                            'is_email_verified', 'telegram_chat_id', 'money', 'premium']

    def get_premium(self, obj):
        premium = Premium.objects.filter(
            payment__user=obj, end_date__gte=datetime.now())
        return PremiumSerializer(premium, many=True, context={'request': self.context['request']}).data

    def get_playlists(self, obj):
        playlists = Playlist.objects.filter(owner=obj)
        return ProfilePlaylistSerializer(playlists, many=True, context={'request': self.context['request']}).data

    def update(self, instance, validated_data):
        try:
            artist_data = validated_data.pop('artist')
            artist = instance.artist
            super().update(artist, artist_data)
        except:
            pass
        return super().update(instance, validated_data)


class PremiumSerializer(serializers.ModelSerializer):
    days = serializers.IntegerField(write_only=True)
    payment = serializers.SerializerMethodField()

    class Meta:
        model = Premium
        fields = ['id', 'start_date', 'end_date',
                  'is_active', 'days_left', 'days', 'payment']
        read_only_fields = ['id', 'start_date', 'end_date',
                            'days_left', 'is_active', 'payment']

    def get_payment(self, obj):
        payment = Payment.objects.filter(pk=obj.payment.pk)
        return PaymentSerializer(payment, many=True, context={'request': self.context['request']}).data

    def validate(self, attrs):
        user = self.context['request'].user
        active_premium = Premium.objects.filter(
            payment__user=user, end_date__gte=datetime.now())

        if attrs['days'] < 1:
            raise serializers.ValidationError({
                'days': ['days must be greater than 0.'],
            })
        if active_premium.exists():
            raise serializers.ValidationError({
                'user': ['You Already Have Premium!'],
            })

        return attrs

    def create(self, validated_data):
        days = validated_data.pop('days')
        validated_data['end_date'] = datetime.now() + timedelta(days=days)
        return super().create(validated_data)


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'user', 'amount', 'date', 'remaining_money']
        read_only_fields = ['id', 'user', 'date', 'remaining_money']

    def validate(self, attrs):
        user_money = self.context['request'].user.money
        is_premium = self.context.get('is_premium')
        money = attrs['amount']
        if user_money + money < 0:
            if is_premium:
                raise serializers.ValidationError({
                    'user': ["You Already Have Premium!"],
                })
            else:
                raise serializers.ValidationError({
                    'amount': [f"You Don't have Enough Charge. Your Money Is {user_money}."],
                })

        return attrs


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
