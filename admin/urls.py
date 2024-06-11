from django.urls import path,include
from .views import AcademyManage ,ToggleIsCertified,PlayerManage,ToggleActive
urlpatterns = [
    path('list_academy', AcademyManage.as_view(), name='list_academy'),
    path('update_certified/<int:id>', ToggleIsCertified.as_view(), name='update_certified'),
    path('list_players', PlayerManage.as_view(),name='list_player'),
    path('toggleIsactive/<int:id>',ToggleActive.as_view(),name='toggleIsactive' )
] 
    