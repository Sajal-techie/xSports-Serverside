from rest_framework.serializers import ModelSerializer
from users.models import UserProfile

class AboutSerializer(ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['about']