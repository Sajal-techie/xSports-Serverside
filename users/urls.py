from django.urls import path,include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import routers
router = routers.DefaultRouter()
from . views import Index
urlpatterns = [
    path('d/', Index.as_view(), name='dd'),
]