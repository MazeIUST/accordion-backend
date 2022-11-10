from django.urls import re_path
from django.contrib.admin.views.decorators import staff_member_required

from .views import SoundCloudAuth, SoundCloudTracks, SoundCloudTrackView

urlpatterns = [
    re_path(r'^$', SoundCloudTracks.as_view(), name='list'),
    re_path(r'^(?P<slug>[\w-]+)/$', SoundCloudTrackView.as_view(), name='detail'),
    re_path(r'^auth/$', staff_member_required(SoundCloudAuth.as_view()), name='auth'),
]
