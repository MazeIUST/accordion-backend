from django.db import models
from django.contrib.auth.models import User, AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_email_verified = models.BooleanField(default=False)
    is_Artist = models.BooleanField(default=False)

    def __str__(self):
        return self.email

class Artist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.user.username
