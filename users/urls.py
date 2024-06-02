from django.urls import path,include
from rest_framework import routers
router = routers.DefaultRouter()
from . views import Signup,VerifyOtp,Login,Profile
urlpatterns = [
    path('signup', Signup.as_view(), name='signup'),
    path('otp_verification',VerifyOtp.as_view(),name='otp_verification'),
    path('login',Login.as_view(),name='login'),
    path('profile',Profile.as_view(),name='profile')
] 