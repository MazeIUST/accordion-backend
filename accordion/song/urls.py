import imp
from django.urls import path
from .views import SongView

urlpatterns = [
    path('', SongView.as_view(), name='songs'),
    path('<int:song_id>/', SongView.as_view(), name='song'),
    path('upload/', SongView.as_view(), name='upload'),
]