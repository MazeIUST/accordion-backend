from django.db import models


class Song(models.Model):
    file = models.FileField(upload_to='songs/files/')

    def __str__(self):
        return self.file.name
