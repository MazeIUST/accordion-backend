from rest_framework.viewsets import ViewSet
from .serializers import UploadSongSerializer
from rest_framework.response import Response


# ViewSets define the view behavior.
class UploadViewSet(ViewSet):
    serializer_class = UploadSongSerializer

    def create(self, request):
        serializer = UploadSongSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response("POST API")
        else:
            return Response(serializer.errors)