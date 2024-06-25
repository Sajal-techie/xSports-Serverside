from rest_framework.serializers import ModelSerializer 
from ..models import Achievements

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
