from rest_framework import generics, permissions
from rest_framework.response import Response
from knox.models import AuthToken
from .serializers import UserSerializer, RegisterSerializer,UpdateUserSerializer
from django.contrib.auth import login
from rest_framework import permissions
from rest_framework.authtoken.serializers import AuthTokenSerializer
from knox.views import LoginView as KnoxLoginView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import Util
import jwt
from .models import User
from django.conf import settings
from django.http import JsonResponse
# from .serializers import MyTokenObtainPairSerializer
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated


# Register API
class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
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
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        })


class LoginAPI(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        # --------- login with email ---------
        username_or_email = request.data.get('username')
        user = User.objects.filter(email=username_or_email)
        if user.exists():
            request.data['username'] = user[0].username
        # ------------------------------------
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        if not user.is_email_verified:
            return Response({'detail': 'Email is not verified'}, status=400)
        # --------- check is login ---------
        token = AuthToken.objects.filter(user=user)
        if token.exists():
            return Response({'detail': 'User is already logged in'}, status=400)
        # ----------------------------------
        login(request, user)
        return super(LoginAPI, self).post(request, format=None)


class VerifyEmail(generics.GenericAPIView):
    serializer_class = RegisterSerializer

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


class UpdateProfileView(generics.UpdateAPIView):

    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = UpdateUserSerializer

# def edit_profile(request):
#     form = prof


def show_all_user(request):
    users = User.objects.all()
    user_list = []
    for user in users:
        new_user = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_email_verified': user.is_email_verified,
            'is_Artist': user.is_Artist
        }
        user_list.append(new_user)
    
    return JsonResponse(user_list, safe=False)


def show_all_user2(request):
    obj_list = []
    for i, user in enumerate(User.objects.all()):
        obj_list.append(user)

    users = UserSerializer(obj_list, many=True).data

    return JsonResponse(users, safe=False) 