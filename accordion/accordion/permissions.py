from rest_framework import permissions

class IsArtist(permissions.BasePermission):
    """
    Global permission check for is artist
    """

    def has_permission(self, request, view):
        is_authenticated = request.user and request.user.is_authenticated
        if is_authenticated:
            return request.user.is_Artist
        return False