from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter


urlpatterns = [
    path('analysis/<int:days>/<str:city>/<str:country>/<int:min_age>/<int:max_age>', HistoryViewSet.as_view({'get': 'analysis'})),
]