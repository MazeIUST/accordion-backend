from django.urls import path
from .views import *
from rest_framework_simplejwt import views as jwt_views
from rest_framework.routers import DefaultRouter


urlpatterns = [
    path('', UrlsView.as_view(), name='urls'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('verify_email/', VerifyEmail.as_view(), name='email-verify'),
    path('profile/', UserViewSet.as_view({'get': 'retrieve', 'put': 'update'}), name='profile'),
    path('profile/all/', UserViewSet.as_view({'get': 'list'}), name='show_all_user'),
    path('profile/<int:pk>/', UserViewSet.as_view({'get': 'retrieve'}), name='show_other_user_profile'),
    path('follow/<int:pk>/', UserViewSet.as_view({'get': 'follow'}), name='follow'),
    path('unfollow/<int:pk>/', UserViewSet.as_view({'get': 'unfollow'}), name='unfollow'),
    path('followers/', UserViewSet.as_view({'get': 'get_followers'}), name='followers'),
    path('followings/', UserViewSet.as_view({'get': 'get_followings'}), name='followings'),
    path('followers/<int:pk>/', UserViewSet.as_view({'get': 'get_followers'}), name='user-followers'),
    path('followings/<int:pk>/', UserViewSet.as_view({'get': 'get_followings'}), name='user-followings'),
    path('change_password/', UserViewSet.as_view({'put': 'change_password'}), name='change_password'),
]
