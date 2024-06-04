from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from users.models import Users,Sport,UserProfile


class SportSerializer(ModelSerializer):
    class Meta:
        model = Sport
        fields = '__all__'
    
class UserProfileSerializer(ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'


class CustomUsersSerializer(ModelSerializer):
    # sport = SportSerializer( write_only = True)
    # profile = UserProfileSerializer(write_only = True)
    class Meta:
        model = Users  
        fields = [
            'username', 'email', 'phone', 'dob', 'is_academy',
             'is_verified', 'password',
        ]
        extra_kwargs = {
            'password' : {'write_only' : True} 
        }
    
    def create(self, validated_data):
        print(validated_data,'validated data......................before')
        # sport = validated_data.pop('sport')
        # profile = validated_data.pop('profile')
        print(validated_data,'validated data......................')
        password = validated_data.pop('password')
        user = Users(**validated_data)
        user.set_password(password)
        user.save()
        
        #creating new instance of sport and userprofile to store sportname 
        # district and state  
        # Sport.objects.create(user=user,**sport)
        # UserProfile.objects.create(user=user,**profile)
        return user 
    