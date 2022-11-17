from rest_framework import permissions

class IsArtist(permissions.BasePermission):
    """
    Global permission check for is artist
    """

    def has_permission(self, request, view):
        is_authenticated = request.user and request.user.is_authenticated
        is_artist = request.user and request.user.is_Artist
        return is_authenticated and is_artist