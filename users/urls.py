from django.urls import path,include
from rest_framework import routers
router = routers.DefaultRouter()
from . views import Signup,VerifyOtp
urlpatterns = [
    path('signup', Signup.as_view(), name='signup'),
    path('otp_verification',VerifyOtp.as_view(),name='otp_verification')
] 