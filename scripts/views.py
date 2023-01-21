from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from .const import *
from accounts.models import *
from song.models import *

from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer


class ScriptView(ViewSet):
    permission_classes = []

    def create_users(self):
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
        return

    def create_followers(self):
        Follow.objects.all().delete()
        All_Users = User.objects.all()
        for user in All_Users:
            for i in range(random.randint(1, 50)):
                user2 = random.choice(All_Users)
                if user != user2:
                    Follow.objects.create(user1=user, user2=user2) if not Follow.objects.filter(
                        user1=user, user2=user2) else None
        print('Followers created successfully')
        return

    def create_tags(self):
        Tag.objects.all().delete()
        for tag in TAGS:
            Tag.objects.create(name=tag)
        print('Tags created successfully')
        return

    def create_song_tags(self):
        songs = Song.objects.all()
        tags = Tag.objects.all()
        for song in songs:
            for i in range(random.randint(1, 5)):
                tag = random.choice(tags)
                song.tags.add(tag)
        print('Song Tags created successfully')
        return

    def create_logs(self):
        All_Users = User.objects.all()
        songs = Song.objects.all()
        for user in All_Users:
            for i in range(random.randint(1, 50)):
                song = random.choice(songs)
                SongLogs.objects.create(user=user, song=song)
        print('Logs created successfully')
        return

    def create_playlists(self):
        All_Users = User.objects.all()
        songs = Song.objects.all()
        for user in All_Users:
            for i in range(random.randint(1, 3)):
                playlist = Playlist.objects.create(owner=user)
                playlist.title = f'Playlist {playlist.pk}'
                playlist.save()
                for i in range(random.randint(1, 10)):
                    song = random.choice(songs)
                    try:
                        PlaylistSong.objects.create(
                            playlist=playlist, song=song)
                    except:
                        pass
        print('Playlists created successfully')
        return

    def main(self, request):
        # self.create_users()
        # self.create_followers()
        # self.create_tags()
        # self.create_song_tags()
        # self.create_logs()
        self.create_playlists()
        return Response({'message': 'All created successfully'})
