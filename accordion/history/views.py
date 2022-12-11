from rest_framework.viewsets import ViewSet
from django.db.models import  F,Q
import datetime
from django.shortcuts import render
from history.models import  History
from song.models import Song,Tag
from accounts.models import User
from rest_framework.response import Response
# Create your views here.

class HistoryViewSet(ViewSet):
    def get_last_day(self, request):
        user = request.user
        today = datetime.datetime.now()
        yesterday = today-datetime.timedelta(days=1)
        user_history =History.objects.filter(user=user,add_datetime__range=[yesterday,today])
        songs_tags = user_history.annotate(tags=F("song_id__tags")).values()
        tags = Tag.objects.all()
        result = {}
        for tag in tags:
            result[tag.id]=0
        for song_tag in songs_tags:
            for tag in song_tag.tags:
                result[tag.id]=+1
        return Response(result)

    def get_last_week(self, request):
        user = request.user
        today = datetime.datetime.now()
        last_week = today-datetime.timedelta(weeks=1)
        user_history =History.objects.filter(user=user,add_datetime__range=[last_week,today])
        songs_tags = user_history.annotate(tags=F("song_id__tags")).values()
        tags = Tag.objects.all()
        result = {}
        for tag in tags:
            result[tag.id]=0
        for song_tag in songs_tags:
            for tag in song_tag.tags:
                result[tag.id]=+1
        return Response(result)

    def get_last_month(self, request):
        user = request.user
        today = datetime.datetime.now()
        last_month = today-datetime.timedelta(days=30)
        user_history =History.objects.filter(user=user,add_datetime__range=[last_month,today])
        songs_tags = user_history.annotate(tags=F("song_id__tags")).values()
        tags = Tag.objects.all()
        result = {}
        for tag in tags:
            result[tag.id]=0
        for song_tag in songs_tags:
            for tag in song_tag.tags:
                result[tag.id]=+1
        return Response(result)

    def get_city_last_day(self,request):
        users = User.objects.all().filter(city=request.data.get('city'))
        today = datetime.datetime.now()
        yesterday = today-datetime.timedelta(days=1)
        users_history =History.objects.filter(add_datetime__range=[yesterday,today],user__in = users)
        songs_tags = users_history.annotate(tags=F("song_id__tags")).values()
        tags = Tag.objects.all()
        result = {}
        for tag in tags:
            result[tag.id]=0
        for song_tag in songs_tags:
            for tag in song_tag.tags:
                result[tag.id]=+1
        return Response(result)
        # songs = Song.objects.filter(id__in=played_songs_id).values



    def get_city_last_week(self,request):
        users = User.objects.all().filter(city=request.data.get('city'))
        today = datetime.datetime.now()
        last_week = today-datetime.timedelta(weeks=1)
        users_history =History.objects.filter(add_datetime__range=[last_week,today],user__in = users)
        songs_tags = users_history.annotate(tags=F("song_id__tags")).values()
        tags = Tag.objects.all()
        result = {}
        for tag in tags:
            result[tag.id]=0
        for song_tag in songs_tags:
            for tag in song_tag.tags:
                result[tag.id]=+1
        return Response(result)
    

    def get_city_last_month(self,request):
        users = User.objects.all().filter(city=request.data.get('city'))
        today = datetime.datetime.now()
        last_month = today-datetime.timedelta(days=30)
        users_history =History.objects.filter(add_datetime__range=[last_month,today],user__in = users)
        songs_tags = users_history.annotate(tags=F("song_id__tags")).values()
        tags = Tag.objects.all()
        result = {}
        for tag in tags:
            result[tag.id]=0
        for song_tag in songs_tags:
            for tag in song_tag.tags:
                result[tag.id]=+1
        return Response(result)