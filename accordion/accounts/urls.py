from django.urls import path
from .views import *
from rest_framework_simplejwt import views as jwt_views
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'profile', UserViewSet, basename='profile')

urlpatterns = [
    path('api/register/', RegisterView.as_view({'post': 'create'}), name='register'),
    path('api/login/', LoginApi.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('verify-email/', VerifyEmail.as_view(), name='email-verify'),
    path('profile/', UserViewSet.as_view({'get': 'retrieve', 'put': 'update'}), name='profile'),
    path('profile/all/', UserViewSet.as_view({'get': 'list'}), name='show_all_user'),
]
