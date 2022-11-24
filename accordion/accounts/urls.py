from django.urls import path
from .views import *
from rest_framework_simplejwt import views as jwt_views
from rest_framework.routers import DefaultRouter


# router = DefaultRouter()
# router.register(r'profile', UserViewSet, basename='profile')
# router.register(r'signup', LoginView, basename='signup')

urlpatterns = [
    path('', UrlsView.as_view(), name='urls'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('verify_email/', VerifyEmail.as_view(), name='email-verify'),
    path('profile/', UserViewSet.as_view({'get': 'retrieve', 'put': 'update'}), name='profile'),
    path('profile/all/', UserViewSet.as_view({'get': 'list'}), name='show_all_user'),
    path('change_password/', UserViewSet.as_view({'put': 'change_password'}), name='change_password'),
]
