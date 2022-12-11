from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter


urlpatterns = [

    path('get_last_day/', HistoryViewSet.as_view({'get': 'get_last_day'}), name='get_last_day'),
    path('get_last_week/', HistoryViewSet.as_view({'get': 'get_last_week'}), name='get_last_week'),
    path('get_last_month/', HistoryViewSet.as_view({'get': 'get_last_month'}), name='get_last_month'),
]