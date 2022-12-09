from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter


urlpatterns = [

    path('get_last_day/', HistoryViewSet.as_view({'get': 'get_last_day'}), name='get_last_day'),
]