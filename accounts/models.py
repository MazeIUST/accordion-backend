import datetime
from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.exceptions import ValidationError


class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_email_verified = models.BooleanField(default=False)
    is_Artist = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    birthday = models.DateField(null=True)
    country = models.CharField(max_length=255, null=True)
    city = models.CharField(max_length=255, null=True)
    bio = models.TextField(null=True)
    image = models.ImageField(
        upload_to='profiles/photos/', default='profiles/photos/default.png')
    telegram_chat_id = models.CharField(
        max_length=255, null=True, blank=True, unique=True)
    money = models.IntegerField(default=0)

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
            'refresh_token': str(refresh),
            'access_token': str(refresh.access_token),
        }

    def update_money(self):
        money = self.payment_set.aggregate(models.Sum('amount'))[
            'amount__sum'] or 0
        self.money = money
        self.save()
        return money


class Artist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    artistic_name = models.CharField(max_length=200, null=True)
    description = models.TextField(null=True)
    activitie_start_date = models.PositiveIntegerField(null=True)

    def __str__(self):
        return self.user.username


class Follow(models.Model):
    user1 = models.ForeignKey(
        User, related_name="user1", on_delete=models.CASCADE)
    user2 = models.ForeignKey(
        User, related_name="user2", on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user1', 'user2')

    def __str__(self):
        return self.user1.username + ' follows ' + self.user2.username


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    remaining_money = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        self.user.update_money()
        self.remaining_money = self.user.money + self.amount
        super(Payment, self).save(*args, **kwargs)
        self.user.update_money()

    def __str__(self):
        return self.user.username


class Premium(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(default=datetime.datetime.now)

    def is_active(self):
        if self.end_date > datetime.datetime.now(tz=datetime.timezone.utc):
            return True
        return False

    def days_left(self):
        return (self.end_date - datetime.datetime.now(tz=datetime.timezone.utc)).days

    def __str__(self):
        return self.user.username
