from django.urls import path,include
from rest_framework import routers
router = routers.DefaultRouter()
from .views import *

urlpatterns = [
    path('profile',ProfileData.as_view(),name='profile'), 
    path('update_photo/<int:id>', UpdatePhoto.as_view(), name='update_photo'),
    path('delete_photo/<int:id>',UpdatePhoto.as_view(),name='delete_photo'),
    path('update_about',UpdateAbout.as_view(),name='update_about'),
    path('user_academy',UserAcademyManage.as_view({'get':'list','post':'create'}),name='user_academy'),
    path('user_academy/<int:id>',UserAcademyManage.as_view({'put':'update','delete':'destroy'}),name='user_academy')
] 