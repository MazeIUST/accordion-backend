from rest_framework import generics
from rest_framework.response import Response
from .serializers import *
from .models import User,Follow
from rest_framework_simplejwt.tokens import RefreshToken # for email
from django.contrib.sites.shortcuts import get_current_site # for email
from django.urls import reverse # for email
from .utils import Util # for email 
import jwt
from django.conf import settings
from django.http import JsonResponse
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ViewSet, ModelViewSet
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404,get_list_or_404
from song.models import *
from song.serializers import *


class UrlsView(APIView):
    permission_classes = []
    authentication_classes = []

    def get(self, request):
        current_site = get_current_site(request).domain
        absurl = 'http://' + current_site + '/'
        account_urls = {
            'user signup': absurl + 'signup/',
            'user login': absurl + 'login/',
            'user logout': absurl + 'logout/',
            'user refresh token': absurl + 'token/refresh/',
            'user verify email': absurl + 'verify_email/',
            'user profile get, put': absurl + 'profile/',
            'user all profile': absurl + 'profile/all/',
            'user other profile': absurl + 'profile/<int:pk>/',
            'user change password': absurl + 'change_password/',
            'user follow': absurl + 'follow/<int:pk>/',
            'user unfollow': absurl + 'unfollow/<int:pk>/',
        }

        songs_urls = {
            'song list': absurl + 'songs/',
            'song get, put, delete': absurl + 'songs/<int:pk>/',
            'song delete all': absurl + 'songs/delete_all/',
            'song search': absurl + 'songs/search/<str:text>/',
            'tag list': absurl + 'songs/tag/',
            'tag get, put, delete': absurl + 'songs/tag/<int:pk>/',
            'playlist list': absurl + 'songs/playlist/',
            'playlist get, put, delete': absurl + 'songs/playlist/<int:pk>/',
            'playlist add song': absurl + 'songs/playlist/add_song/<int:pk>/',
            'playlist remove song': absurl + 'songs/playlist/remove_song/<int:pk>/',
            'playlist 3 public': absurl + 'songs/playlist/home/',
        }

        return Response({'account_urls': account_urls, 'songs_urls': songs_urls})
        

class SignUpView(APIView):
    serializer_class = SignUpSerializer
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # --------- send email ---------
        token = RefreshToken.for_user(user)
        current_site = get_current_site(request).domain
        relativeLink = reverse('email-verify')
        absurl = 'http://' + current_site + relativeLink + "?token=" + str(token)
        print(absurl)
        email_body = 'Hi ' + user.username + ' Use link below to verify your email\n' + absurl
        data = {
            'email_body': email_body,
            'to_email': user.email,
            'email_subject': 'Verify your email'
        }
        Util.send_email(data)
        # ------------------------------
        return Response({
            "user": UserSerializer(user).data,
            "message": "User Created Successfully. Now perform Login to get your token",
        })


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer
    permission_classes = []
    authentication_classes = []

    def change_username_to_email(self, request, *args, **kwargs):
        username = request.data.get('username')
        user = User.objects.filter(email=username)
        if user.exists():
            _mutable = request.data._mutable
            request.data._mutable = True        
            request.data['username'] = user[0].username
            request.data._mutable = _mutable
        return None      

    def post(self, request, *args, **kwargs):
        self.change_username_to_email(request)
        username = request.data.get('username')
        user = User.objects.filter(username=username)
        if user.exists():
            user = user.get(username=username)
            login(request, user)
        return super().post(request, *args, **kwargs)
        

class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'change_password':
            return ChangePasswordSerializer
        return UserSerializer
    
    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.action == 'retrieve_other_user':
            permission_classes = []
        return [permission() for permission in permission_classes]
   
    def list(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def retrieve(self, request):
        user = UserSerializer(request.user).data
        return Response(user, status=status.HTTP_200_OK) 

    def update(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)   

    def change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.update(request.user, serializer.validated_data)
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve_other_user(self, request, pk=None):
        user = get_object_or_404(User, id=pk)
        user_serializer = UserPublicSerializer(user)
        return Response(user_serializer.data, status=status.HTTP_200_OK)

    def follow(self, request, pk=None):
        user_to_follow = get_object_or_404(User, id=pk)
        user = request.user
        if user_to_follow == user:
            return Response({'error': 'You cannot follow yourself'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            Follow.objects.get_or_create(user1=user, user2=user_to_follow)
            return Response({'message': 'You are now following ' + user_to_follow.username}, status=status.HTTP_200_OK)
            
    def unfollow(self, request, pk=None):
        user_to_unfollow = get_object_or_404(User, id=pk)
        user = request.user
        if user_to_unfollow == user:
            return Response({'error': 'You cannot unfollow yourself'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            Follow.objects.filter(user1=user, user2=user_to_unfollow).delete()
            return Response({'message': 'You are no longer following ' + user_to_unfollow.username}, status=status.HTTP_200_OK)


    def get_recent_10_music(self, request):
        user = UserSerializer(request.user).data.get('id')
        user_history =History.objects.get(user=user).order_by('-add_datetime').distinct('song_id')[:10] # if less than 10 tracks
        recent_10_music =user_history.values('song_id').to_dict()
        return Response(recent_10_music)

    def get_recent_10_artist(self, request):
        user = UserSerializer(request.user).data.get('id')
        user_history =History.objects.get(user=user).order_by('-add_datetime').distinct('song__artist')[:10] # if less than 10 tracks
        recent_10_artist =user_history.values('song__artist_id').to_dict()
        return Response(recent_10_artist)
    

class VerifyEmail(generics.GenericAPIView):
    permission_classes = []
    authentication_classes = []

    def get(self, request):
        token = request.GET.get('token')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id=payload['user_id'])
            if not user.is_email_verified:
                user.is_email_verified = True
                user.save()
            return Response({'email': 'Successfully activated'}, status=200)
        except jwt.ExpiredSignatureError as identifier:
            return Response({'error': 'Activation Expired'}, status=400)
        except jwt.exceptions.DecodeError as identifier:
            return Response({'error': 'Invalid token'}, status=400)

class LogoutView(APIView):

    def get(self, request):
        logout(request)
        return Response(status=status.HTTP_200_OK)

