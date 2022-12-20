from rest_framework import generics
from rest_framework.response import Response
from .serializers import *
from .models import User, Follow
from rest_framework_simplejwt.tokens import RefreshToken  # for email
from django.contrib.sites.shortcuts import get_current_site  # for email
from django.urls import reverse  # for email
from .utils import Util  # for email
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
from django.shortcuts import get_object_or_404, get_list_or_404
from song.models import *
from song.serializers import *
from datetime import datetime
from django.db.models import F, Q


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
            'user get followers': absurl + 'followers/',
            'user get followings': absurl + 'followings/',
            'user get followers of other user': absurl + 'followers/<int:pk>/',
            'user get followings of other user': absurl + 'followings/<int:pk>/',
            'user payment': absurl + 'payment/',
            'user payment get': absurl + 'payment/<int:pk>/',
            'user permium': absurl + 'permium/',
        }

        songs_urls = {
            'song list, create': absurl + 'songs/',
            'song get, put, delete': absurl + 'songs/<int:pk>/',
            'song delete all': absurl + 'songs/delete_all/',
            'song search': absurl + 'songs/search/<str:text>/',
            'tag list': absurl + 'songs/tag/',
            'tag get, put, delete': absurl + 'songs/tag/<int:pk>/',
            'playlist list, create': absurl + 'songs/playlist/',
            'playlist get, put, delete': absurl + 'songs/playlist/<int:pk>/',
            'playlist add song': absurl + 'songs/playlist/<int:pk>/add_song/',
            'playlist remove song': absurl + 'songs/playlist/<int:playlist_pk>/remove_song/<int:song_pk>/',
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
        absurl = 'http://' + current_site + \
            relativeLink + "?token=" + str(token)
        print(absurl)
        email_body = 'Hi ' + user.username + \
            ' Use link below to verify your email\n' + absurl
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
        return UserPrivateSerializer

    def list(self, request):
        users = User.objects.all()
        serializer = UserSerializer(
            users, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        if pk:
            serializer = UserSerializer(get_object_or_404(
                User, pk=pk), context={'request': request}).data
        else:
            serializer = UserPrivateSerializer(
                request.user, context={'request': request}).data
        return Response(serializer, status=status.HTTP_200_OK)

    def update(self, request):
        serializer = UserPrivateSerializer(
            request.user, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def change_password(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.update(request.user, serializer.validated_data)
        return Response({'message': 'Password updated successfully'}, status=status.HTTP_200_OK)


class FollowViewSet(ViewSet):

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

    def get_followers(self, request, pk=None):
        user = get_object_or_404(User, id=pk) if pk else request.user
        followers = Follow.objects.filter(user2=user)
        followers_serializer = FollowerSerializer(
            followers, many=True, context={'request': request})
        return Response(followers_serializer.data, status=status.HTTP_200_OK)

    def get_followings(self, request, pk=None):
        user = get_object_or_404(User, id=pk) if pk else request.user
        followings = Follow.objects.filter(user1=user)
        followings_serializer = FollowingSerializer(
            followings, many=True, context={'request': request})
        return Response(followings_serializer.data, status=status.HTTP_200_OK)


class PermiumViewSet(ViewSet):
    serializer_class = PermiumSerializer

    def create(self, request):
        _mutable = request.data._mutable
        request.data._mutable = True
        request.data['days'] = int(request.data.get('days'))
        request.data._mutable = _mutable
        amount = request.data.get('days') * 100
        payment_serializer = PaymentSerializer(
            data={'amount': -1*amount}, context={'request': request})
        payment_serializer.is_valid(raise_exception=True)
        payment = payment_serializer.save(user=request.user)
        serializer = PermiumSerializer(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(payment=payment)
        else:
            payment.delete()
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Permium created successfully'}, status=status.HTTP_200_OK)

    def retrieve(self, request):
        permiums = Permium.objects.filter(
            payment__user=request.user, end_date__gte=datetime.now())
        serializer = PermiumSerializer(
            permiums, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request):
        permium = Permium.objects.filter(user=request.user)
        serializer = PermiumSerializer(
            permium, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class PaymentViewSet(ViewSet):
    serializer_class = PaymentSerializer

    def create(self, request):
        serializer = PaymentSerializer(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response({
            'message': f'Payment created successfully. your money is {request.user.money}',
            'money': request.user.money
        }, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        payment = get_object_or_404(Payment, id=pk)
        serializer = PaymentSerializer(payment, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request):
        payment = Payment.objects.filter(user=request.user)
        serializer = PaymentSerializer(payment, many=True, context={
                                       'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class VerifyEmail(generics.GenericAPIView):
    permission_classes = []
    authentication_classes = []

    def get(self, request):
        token = request.GET.get('token')
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=['HS256'])
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
