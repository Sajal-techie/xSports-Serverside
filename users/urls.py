from django.urls import path,include
from rest_framework import routers
router = routers.DefaultRouter()
from . views import Signup,VerifyOtp,Login,Logout,ResendOtp
urlpatterns = [
    path('signup', Signup.as_view(), name='signup'),
    path('otp_verification',VerifyOtp.as_view(),name='otp_verification'),
    path('login',Login.as_view(),name='login'),
    path('logout',Logout.as_view(),name='logout'),
    path('resend_otp',ResendOtp.as_view(),name='resend_otp') 
] 