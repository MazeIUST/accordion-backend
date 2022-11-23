from rest_framework import generics
from rest_framework.response import Response
from .serializers import *
from .models import User
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
from rest_framework.viewsets import ViewSet
from rest_framework import status
from django.contrib.auth import authenticate, login


#Register API
class RegisterView(ViewSet):
    serializer_class = RegisterSerializer
    permission_classes = []
    authentication_classes = []

    def create(self, request):
        serializer = RegisterSerializer(data=request.data)
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


class UserViewSet(ViewSet):
    serializer_class = UserSerializer

    def list(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


    def retrieve(self, request):
        content = UserSerializer(request.user).data
        return Response(content) 


    def update(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)     


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


class LoginApi(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
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

