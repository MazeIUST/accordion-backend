from django.db import models
from accounts.models import Artist,User


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
    image = models.ImageField(upload_to='songs/images/', blank=True, null=True)
    note = models.FileField(upload_to='songs/notes/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return self.title

class Playlist(models.Model):
    title = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    songs = models.ManyToManyField(Song, blank=True)
    description = models.TextField(null=True, blank=True)
    is_public = models.BooleanField(default=True)
    image = models.ImageField(null=True, blank=True,upload_to='playlists/photos/')
    def str(self):
        return self.title