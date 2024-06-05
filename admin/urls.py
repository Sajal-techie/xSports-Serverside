from django.urls import path,include
from .views import AcademyManage ,ToggleIsCertified
urlpatterns = [
    path('list_academy', AcademyManage.as_view(), name='list_academy'),
    path('update_certified/<str:id>', ToggleIsCertified.as_view(), name='update_certified'),
] 
   