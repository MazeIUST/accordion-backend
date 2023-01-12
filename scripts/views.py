from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from .const import *
from accounts.models import *
from song.models import *


class UserViewSet(ViewSet):
    def create_users(request):
        User.objects.all().delete()
        All_Users = make_user()
        for user_data in All_Users:
            try:
                User.objects.create(**user_data)
                if user_data['is_Artist']:
                    Artist.objects.create(user=User.objects.get(
                        username=user_data['username']))
            except:
                print('Error while creating user: ', user_data['username'])

        print('Users created successfully')
        return Response({'message': 'Users created successfully'})


class FollowViewSet(ViewSet):
    def create_followers(request):
        Follow.objects.all().delete()
        All_Users = User.objects.all()
        for user in All_Users:
            for i in range(random.randint(1, 50)):
                user2 = random.choice(All_Users)
                if user != user2:
                    Follow.objects.create(user1=user, user2=user2)
        print('Followers created successfully')
        return Response({'message': 'Followers created successfully'})


class TagViewSet(ViewSet):
    def create_tags(request):
        Tag.objects.all().delete()
        for tag in TAGS:
            Tag.objects.create(name=tag)
        print('Tags created successfully')
        return Response({'message': 'Tags created successfully'})
