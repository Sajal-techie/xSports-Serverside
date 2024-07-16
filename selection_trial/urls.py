from django.urls import path
from rest_framework import routers
router = routers.DefaultRouter()
from .views import *

players_in_trial_list = PlayersInTrialViewSet.as_view({
    'get': 'list_players_in_trial'
})
trial_player_details = TrialViewSet.as_view({
    'get':'player_detials_in_trial'
})


urlpatterns = [
    path('trial',TrialViewSet.as_view({'get':'list','post':'create'}),name='trial'), 
    path('trial/<int:id>',TrialViewSet.as_view({'get':'retrieve','put':'update','delete':'destroy'}),name='trial'), 
    path('trial/<int:id>/',TrialViewSet.as_view({'delete':'destroy'}),name='trial'), 
    path('player_trial', PlayersInTrialViewSet.as_view({'get':'list','post':'create',}), name='player_trial'),
    path('player_trial/<int:id>',PlayersInTrialViewSet.as_view({'get':'retrieve','put':'update','delete':'destroy', 'patch': 'partial_update'}),name='player_trial'),
    path('players_in_trial_list/<int:trial_id>', players_in_trial_list, name='players_in_trial_list'),
    path('trial_player_details/<int:id>', trial_player_details, name='trial_player_details'),
    path('trial_history',TrialHistory.as_view(),name='trial_history'),
    # path('create_checkout_session/<int:id>',StripeCheckoutView.as_view(),name='create_checkout_session'),
    # path("webhook_test", WebHook.as_view(), name="webhook_test")
] 