from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from .serializers import SongSerializer
import os
from django.conf import settings
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from .models import Song
# FileResponse
from django.http import FileResponse

class SongViewSet(ViewSet):
    serializer_class = SongSerializer
    permission_classes = []

    def download_song(self, request, pk):
        song = get_object_or_404(Song, pk=pk)
        file_path = os.path.join(settings.MEDIA_ROOT, song.file.name)
        if os.path.exists(file_path):
            return FileResponse(open(file_path, 'rb'), as_attachment=True)
        raise Http404

    def create(self, request):
        serializer = SongSerializer(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)
