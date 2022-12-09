from rest_framework.viewsets import ViewSet
from django.db.models import  F,Q
import datetime
from django.shortcuts import render
from history.models import  History
from song.models import Song,Tag
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
        # result = []
        result = {}
        for tag in tags:
            count = songs_tags.filter(tags__contains =tag ).count() # ارور میده که تگ رو نمیتونه مساوی قرار بده باید استرینگ یا اینت باشه
            result[tag]= count
        return Response(result)



        # songs = Song.objects.filter(id__in=played_songs_id).values