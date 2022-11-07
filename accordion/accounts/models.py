from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.conf import settings
from django_countries.fields import CountryField
from birthday import BirthdayField, BirthdayManager

class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_email_verified = models.BooleanField(default=False)
    is_Artist = models.BooleanField(default=False)

    Name = models.CharField(max_length=255)
    Birthday = BirthdayField()
    # objects = BirthdayManager()
    Country = CountryField()

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
    
class Artist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.user.username
