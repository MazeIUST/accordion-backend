from rest_framework import permissions
from rest_framework.permissions import IsAdminUser

class IsSuperUser(IsAdminUser):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


class IsArtist(permissions.BasePermission):
    """
    Global permission check for is artist
    """

    def has_permission(self, request, view):
        is_authenticated = request.user and request.user.is_authenticated
        if is_authenticated:
            return request.user.is_Artist
        return False

    def has_object_permission(self, request, view, obj):
        if view.action in ['update', 'destroy']:
            if obj.artist.user == request.user or request.user.is_superuser:
                return True
            return False
        return True