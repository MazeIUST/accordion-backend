from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
# Create your models here.


class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_email_verified = models.BooleanField(default=False)
    is_Artist = models.BooleanField(default=False)
    birthday = models.DateField(null=True)
    country = models.CharField(max_length=255,null=True)
    image_url = models.ImageField(upload_to='profiles/photos/', blank=True, null=True)

    GENDER_Male = 'M'
    GENDER_Female = 'F'
    GENDER_PreferNotToSay = 'P'
    GENDER_Other = 'O'
    GENDER_CHOICES = [
        (GENDER_Female, 'Female'),
        (GENDER_Male, 'Male'),
        (GENDER_PreferNotToSay, 'Prefer not to say'),
        (GENDER_Other, 'Other'),
    ]
    gender = models.CharField(
        max_length=1, choices=GENDER_CHOICES, default=GENDER_PreferNotToSay)

    def __str__(self):
        return self.email
    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh_token':str(refresh),
            'access_token':str(refresh.access_token),
        }


class Artist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    artistic_name = models.CharField(max_length=200,null=True)
    activitie_start_date = models.Date(null=True)
    
    def __str__(self):
        return self.user.username

        