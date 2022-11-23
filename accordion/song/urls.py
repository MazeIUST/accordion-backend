from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'admin', SongViewSet_Admin, basename='admin')
router.register(r'artist', SongViewSet_Artist, basename='artist')
router.register(r'user', SongViewSet_User, basename='user')
router.register(r'', SongViewSet, basename='songs')
router.register(r'tag', TagViewSet, basename='tag')


urlpatterns = [
    path('', SongViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('<int:pk>/', SongViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),
    path('delete_all/', SongViewSet.as_view({'delete': 'delete_all'})),
    path('search/<str:text>/', SongViewSet.as_view({'get': 'search'}), name='song_search'),

    path('admin/', SongViewSet_Admin.as_view({'get': 'list'})),
    path('admin/<int:pk>/', SongViewSet_Admin.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),
    path('admin/delete_all/', SongViewSet_Admin.as_view({'delete': 'destroy_all'})),

    path('artist/', SongViewSet_Artist.as_view({'get': 'list', 'post': 'create'})),
    path('artist/<int:pk>/', SongViewSet_Artist.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),
    path('artist/zahra/', ZahraViewSet.as_view({'post': 'create'}), name='zahra'),

    path('user/', SongViewSet_User.as_view({'get': 'list'}), name='songs'),
    path('user/<int:pk>/', SongViewSet_User.as_view({'get': 'retrieve'}), name='song'),
    path('user/search/<str:text>/', SongViewSet_User.as_view({'get': 'search'}), name='song_search'),

    path('tag/', TagViewSet.as_view({'get': 'list', 'post': 'create'}), name='tags'),
    path('tag/<int:pk>/', TagViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='tag'),

]