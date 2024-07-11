from django.urls import path
from rest_framework import routers
router = routers.DefaultRouter()
from .views import *

urlpatterns = [
    path('trial',TrialViewSet.as_view({'get':'list','post':'create',}),name='trial'), 
    path('trial/<int:id>',TrialViewSet.as_view({'get':'retrieve','put':'update','delete':'destroy'}),name='trial'), 
    path('player_trial', PlayersInTrialViewSet.as_view({'get':'list','post':'create',}), name='player_trial'),
    path('player_trial/<int:id>',PlayersInTrialViewSet.as_view({'get':'retrieve','put':'update','delete':'destroy'}),name='player_trial'),
    path('player_exist/<int:id>',PlayerExistInTrialView.as_view(),name='player_exist'),
    # path('user_academy',UserAcademyManage.as_view({'get':'list','post':'create'}),name='user_academy'),
    # path('user_academy/<int:id>',UserAcademyManage.as_view({'put':'update','delete':'destroy'}),name='user_academy'),
    # path('user_achievement',AchievementManage.as_view({'get':'list','post':'create'}),name='user_achievement'),
    # path('user_achievement/<int:id>',AchievementManage.as_view({'put':'update','delete':'destroy'}),name='user_achievement'),
] 