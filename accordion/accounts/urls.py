from .views import RegisterAPI
from django.urls import path
from knox import views as knox_views
from .views import *
from django.urls import path

urlpatterns = [
    path('api/register/', RegisterAPI.as_view(), name='register'),
    path('api/login/', LoginAPI.as_view(), name='login'),
    path('api/logout/', knox_views.LogoutView.as_view(), name='logout'),
    path('api/logoutall/', knox_views.LogoutAllView.as_view(), name='logoutall'),
    path('verify-email/', VerifyEmail.as_view(), name='email-verify'),

]

