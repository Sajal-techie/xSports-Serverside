from rest_framework.serializers import ModelSerializer 
from ..models import Achievements
import os

class AchievementSerializer(ModelSerializer):
    class Meta:
        model = Achievements
        fields = ['id','title','issued_by','issued_month','issued_year','image','description','user']
    
    def validate_image(self,value):
        print(value)
        return value
    
    def create(self, validated_data):
        user = self.context['request'].user
        print(validated_data)
        return Achievements.objects.create(user=user,**validated_data)

    def update(self, instance, validated_data):
        print(instance.image.path,'instance in update')
        if instance.image and os.path.exists(instance.image.path):
            os.remove(instance.image.path)
        return super().update(instance, validated_data)