from django.shortcuts import render

# Create your views here.
from rest_framework import generics, permissions
from rest_framework.response import Response
from knox.models import AuthToken
from .serializers import UserSerializer, RegisterSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .utils import Util
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
import jwt
from django.conf import settings
from .models import User
# Register API
class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()


        token = RefreshToken.for_user(user)

        current_site = get_current_site(request).domain
        relativeLink=reverse('email-verify')
        


        absurl = 'http://'+current_site+relativeLink+'?token='+ str(token)
        email_body='Hi' + user.username + '.Use link below to verify your email\n' + absurl
        data = {
            # 'domain': absurl,
            'to_email' : user.email,
            'email_body': email_body,
            'email_subject': 'verify your email address'
        }
        Util.send_email(data)


        return Response({
        "user": UserSerializer(user, context=self.get_serializer_context()).data,
        "token": AuthToken.objects.create(user)[1]
        })


class VerifyEmail(generics.GenericAPIView):
    def get(self,request):
        token = request.GET.get('token')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            print(payload)
            user = User.objects.get(id=payload['user_id'])
            if not user.is_email_verified:
                user.is_email_verified = True
                user.save()
            return Response({'email': 'Successfully activated'}, status=200)
        except jwt.ExpiredSignatureError as identifier:
            return Response({'error': 'Activation Expired'}, status=400)
        except jwt.exceptions.DecodeError as identifier:
            return Response({'error': 'Invalid token'}, status=400)


from django.contrib.auth import login

from rest_framework import permissions
from rest_framework.authtoken.serializers import AuthTokenSerializer
from knox.views import LoginView as KnoxLoginView

class LoginAPI(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return super(LoginAPI, self).post(request, format=None)