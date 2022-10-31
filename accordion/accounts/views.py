from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    UserModel View.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()


@csrf_exempt
def signup(request):
    if request.method == 'POST':
        data = request.POST   
        print(data)         
        new_user = {
            'username': data.get('username'),
            'password': data.get('password'),
            'email': data.get('email'),
            'first_name': data.get('first_name'),
            'last_name': data.get('last_name'),
        }
        user = User(username=new_user['username'], email=new_user['email'], first_name=new_user['first_name'], last_name=new_user['last_name'])
        user.save()
        return JsonResponse({'status': 'User created successfully'})
    return JsonResponse({'status': 'Get Method not allowed'})