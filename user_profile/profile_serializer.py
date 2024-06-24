from rest_framework.serializers import ModelSerializer,Serializer
from rest_framework import serializers
from users.models import UserProfile,Users
from .models import UserAcademy

class AboutSerializer(ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['about']

class AcademyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['profile_photo']
        
class AcademyDetailSerialiezer(serializers.ModelSerializer): 
    profile = AcademyProfileSerializer(source='userprofile',read_only=True)
    class Meta:
        model = Users
        fields = ['id','username','profile'] 

class UserAcademySerializer(ModelSerializer):
    academy_details = AcademyDetailSerialiezer(source='academy',read_only=True,required=False)
    class Meta:
        model = UserAcademy
        fields = ['id','academy', 'start_month', 'start_year', 'end_month', 'end_year','position', 'is_current', 'sport','academy_details']
    
    def validate(self, attrs):
        print(attrs,'validate')
        if 'is_current' in attrs:
            if attrs['is_current']:
                attrs['end_month'] = ''
                attrs['end_year'] = ''
        if 'start_month' not in attrs:
            raise serializers.ValidationError({"message":"Enter valid Start Month"})
        elif 'start_year' not in attrs:
            raise serializers.ValidationError({"message":"Enter valid start year"})
        elif 'sport' not in attrs:
            raise serializers.ValidationError({"message":"Enter valid sport"})
        elif 'position' not in attrs:
            raise serializers.ValidationError({"message":"Enter valid position"})
        return attrs
    def validate_academy(self, value):
        print(value,'validate academy')
        if value is None:
            raise serializers.ValidationError({"message":"Enter valid academy"})
        return value


    def create(self, validated_data):
        print(validated_data,'\n',self.context['request'].user)
        user = self.context['request'].user
        return UserAcademy.objects.create(user=user, **validated_data) 