from django.urls import path
from .views import *
from rest_framework_simplejwt import views as jwt_views

urlpatterns = [
    path('api/register/', RegisterApi.as_view(),name='register'),
    path('api/login/', LoginApi.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('verify-email/', VerifyEmail.as_view(), name='email-verify'),
    path('show_all_user/', show_all_user2, name="show_all_user"),
]
