from django.db import models
from accounts.models import *
from song.models import *
# Create your models here.


class History(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    add_datetime = models.DateTimeField(auto_now_add=True)
    # location 


