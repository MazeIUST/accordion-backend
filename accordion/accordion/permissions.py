from rest_framework import permissions
from rest_framework.permissions import IsAdminUser
from rest_framework.permissions import IsAuthenticated

class IsSuperUser(IsAdminUser):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


class IsArtist(permissions.BasePermission):

    def has_permission(self, request, view):
        is_authenticated = request.user and request.user.is_authenticated
        if is_authenticated:
            return request.user.is_Artist
        return False

    def has_object_permission(self, request, view, obj):
        if view.action in ['update', 'destroy']:
            if obj.artist.user == request.user:
                return True
            return False
        return True

class IsArtistORSuperuser(permissions.BasePermission):

    def has_permission(self, request, view):
        is_authenticated = request.user and request.user.is_authenticated
        if is_authenticated:
            return request.user.is_Artist or request.user.is_superuser
        return False

    def has_object_permission(self, request, view, obj):
        if view.action in ['update', 'destroy']:
            return request.user.is_superuser or obj.artist.user == request.user
        return True