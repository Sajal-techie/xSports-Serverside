from rest_framework.serializers import ModelSerializer,Serializer
from rest_framework import serializers
from users.models import UserProfile

class AboutSerializer(ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['about']
 