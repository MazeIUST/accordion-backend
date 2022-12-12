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
    def analysis(self, request, days=None, city=None, country=None, min_age=None, max_age=None):
        today = datetime.datetime.now()
        last_time = today-datetime.timedelta(days=days)
        days_filter = Q(add_datetime__range=[last_time,today]) if days!= 0 else Q()
        city_filter = Q(user__city=city) if city!= '0' else Q()
        country_filter = Q(user__country=country) if country!= '0' else Q()
        min_age_filter = Q(user__birthday__lte=today-datetime.timedelta(days=min_age*365)) if min_age!= 0 else Q()
        max_age_filter = Q(user__birthday__gte=today-datetime.timedelta(days=max_age*365)) if max_age!= 0 else Q()
        user_history =History.objects.filter(days_filter,city_filter,country_filter,min_age_filter,max_age_filter)
        songs_tags = user_history.annotate(tags=F("song_id__tags")).values()
        tags = Tag.objects.all()
        result = {}
        for tag in tags:
            result[tag.id]=0
        for song_tag in songs_tags:
            for tag in song_tag.tags:
                result[tag.id]=+1
        return Response(result)

