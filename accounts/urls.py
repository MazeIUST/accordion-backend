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
    path('profile/',
         UserViewSet.as_view({'get': 'retrieve', 'put': 'update'}), name='profile'),
    path('profile/all/',
         UserViewSet.as_view({'get': 'list'}), name='show_all_user'),
    path('profile/<int:pk>/',
         UserViewSet.as_view({'get': 'retrieve'}), name='show_other_user_profile'),
    path('profile/<str:pk>/',
         UserViewSet.as_view({'get': 'retrieve'}), name='show_other_user_profile_by_username'),
    path('follow/<int:pk>/',
         FollowViewSet.as_view({'get': 'follow'}), name='follow'),
    path('unfollow/<int:pk>/',
         FollowViewSet.as_view({'get': 'unfollow'}), name='unfollow'),
    path('followers/',
         FollowViewSet.as_view({'get': 'get_followers'}), name='followers'),
    path('followings/',
         FollowViewSet.as_view({'get': 'get_followings'}), name='followings'),
    path('followers/<int:pk>/',
         FollowViewSet.as_view({'get': 'get_followers'}), name='user-followers'),
    path('followings/<int:pk>/',
         FollowViewSet.as_view({'get': 'get_followings'}), name='user-followings'),
    path('change_password/',
         UserViewSet.as_view({'patch': 'change_password'}), name='change_password'),
    path('payment/',
         PaymentViewSet.as_view({'post': 'create', 'get': 'list'}), name='payment'),
    path('payment/<int:pk>/',
         PaymentViewSet.as_view({'get': 'retrieve'}), name='get_payment'),
    path('premium/',
         PremiumViewSet.as_view({'post': 'create', 'get': 'retrieve'}), name='premium'),
]
