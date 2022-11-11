# from django.conf.urls import url
from django.urls import path, include
from .views import *

urlpatterns = [
    path('api/register/', RegisterApi.as_view(),name='register'),
    path('api/login/', LoginAPIview.as_view(),name='login'),
    path('verify-email/', VerifyEmail.as_view(), name='email-verify'),
    path('show_all_user/', show_all_user2, name="show_all_user"),
]
