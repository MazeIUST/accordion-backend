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

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','username', 'first_name','last_name', 'birthday', 'country','gender','image_url','email')
        read_only_fields = ('id', 'email')

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        # Add extra responses here
        # data['name'] = self.user.name
        # ...

        is_email_verified = self.user.is_email_verified
        if not is_email_verified:
            raise serializers.ValidationError({
                'email': ['email is not verified.'],
            })

        return data