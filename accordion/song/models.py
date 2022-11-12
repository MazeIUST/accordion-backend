from django.db import models
from accounts.models import Artist

class Song(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    song = models.FileField(upload_to='media/songs/songs/', null=True, blank=True)
    image = models.ImageField(upload_to='media/songs/images/', blank=True, null=True)
    note = models.FileField(upload_to='media/songs/notes/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
