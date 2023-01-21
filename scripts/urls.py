from django.urls import path
from .views import *


urlpatterns = [
    path('all/', ScriptView.as_view({'get': 'main'}), name='script_all'),
]
