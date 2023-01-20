from django.shortcuts import render
from .models import Song
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from .serializers import SongSerializer


class SongViewSet(ViewSet):
    serializer_class = SongSerializer

    def create(self, request):
        serializer = self.serializer_class(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)
