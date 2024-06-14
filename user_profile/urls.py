from django.urls import path,include
from rest_framework import routers
router = routers.DefaultRouter()
from .views import *

urlpatterns = [
    path('profile',ProfileData.as_view(),name='profile'), 
    path('update_photo/<int:id>', UpdatePhoto.as_view(), name='update_photo'),
    path('delete_photo/<int:id>',UpdatePhoto.as_view(),name='delete_photo'),
    # path('profile',ProfileData.as_view(),name='profile'),
    # path('resend_otp',ResendOtp.as_view(),name='resend_otp')
] 