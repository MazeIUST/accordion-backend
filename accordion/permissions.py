from rest_framework import permissions
from rest_framework.permissions import IsAdminUser
from rest_framework.permissions import IsAuthenticated


class IsSuperUser(IsAdminUser):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


class IsArtist(permissions.BasePermission):

    def has_permission(self, request, view):
        is_authenticated = request.user and request.user.is_authenticated
        return request.user.is_Artist if is_authenticated else False

    def has_object_permission(self, request, view, obj):
        return bool(obj.artist.user == request.user)


class IsAlbumOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return bool(request.user.is_superuser or obj.artist.user == request.user)


class IsArtistORSuperuser(permissions.BasePermission):

    def has_permission(self, request, view):
        is_authenticated = request.user and request.user.is_authenticated
        return request.user.is_Artist if is_authenticated else False

    def has_object_permission(self, request, view, obj):
        return bool(request.user.is_superuser or obj.artist.user == request.user)


class IsPlaylistOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return bool(request.user.is_superuser or obj.owner == request.user)


class IsPublicPlaylist(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return bool(request.user.is_superuser or obj.owner == request.user or obj.is_public)
