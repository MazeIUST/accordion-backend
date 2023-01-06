from rest_framework.response import Response
from accounts.models import *
from rest_framework.viewsets import ViewSet

from .const import USERS



class UserViewSet(ViewSet):
    def create_users(request):
        User.objects.all().delete()
        for user_data in USERS:
            try:
                User.objects.create(**user_data)
                if user_data['is_Artist']:
                    Artist.objects.create(user=User.objects.get(
                        username=user_data['username']))
            except:
                print('Error while creating user: ', user_data['username'])

        print('Users created successfully')
        return Response({'message': 'Users created successfully'})
    
    
    
    


