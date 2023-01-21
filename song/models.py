import datetime
from django.db import models
from accounts.models import Artist, User


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Song(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    lyrics = models.TextField(null=True, blank=True)
    song_link = models.CharField(max_length=1000)
    speechless_song_link = models.CharField(max_length=1000, null=True)
    image = models.ImageField(upload_to='songs/images/', blank=True, null=True)
    note = models.FileField(upload_to='songs/notes/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name='tags')
    count = models.IntegerField(default=0)
    telegram_id = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.title


class Playlist(models.Model):
    title = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(null=True, blank=True)
    is_public = models.BooleanField(default=True)
    image = models.ImageField(null=True, blank=True,
                              upload_to='playlists/photos/')

    class Meta:
        unique_together = ('title', 'owner')

    def str(self):
        return self.title


class SongLogs(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} - {self.song}'


class PlaylistSong(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('playlist', 'song')

    def __str__(self):
        return f'{self.playlist} - {self.song}'


class Album(models.Model):
    title = models.CharField(max_length=100)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(null=True, blank=True,
                              upload_to='albums/photos/')

    def str(self):
        return self.title


class AlbumSong(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('album', 'song')

    def __str__(self):
        return f'{self.album} - {self.song}'
