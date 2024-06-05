from rest_framework.serializers import ModelSerializer,Serializer
from rest_framework import serializers
from users.models import Users,Sport,UserProfile,Academy


class SportSerializer(ModelSerializer):
    class Meta:
        model = Sport
        fields = ['sport_name']
    
class UserProfileSerializer(ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['bio','state','district','about','profile_photo','cover_photo']
 

class CustomUsersSerializer(ModelSerializer):
    sport = serializers.CharField(max_length=255,required=False)
    district = serializers.CharField(max_length=255,required=False)
    state = serializers.CharField(max_length=255,required=False)
    license = serializers.FileField(required=False) 
    sports = SportSerializer(read_only =True)
    user_profile= UserProfileSerializer(read_only=True)

    class Meta: 
        model = Users  
        fields = [
            'username', 'email', 'phone', 'dob', 'is_academy',
             'is_verified', 'password','sport','district','state','license','sports','user_profile'
        ]
        extra_kwargs = {
            'password' : {'write_only' : True} 
        }
    
    def create(self, validated_data):
        print(validated_data,'validated data......................before')
        sport = validated_data.pop('sport')
        state = validated_data.pop('state')
        district = validated_data.pop('district')
        license = validated_data.pop('license',None)
        print(validated_data,'validated data......................after',sport,state,district,license)
        password = validated_data.pop('password')
        instance = super().create(validated_data)
        instance.set_password(password)
        instance.save()
        
        '''creating new instance of sport and userprofile to store sportname 
         district and state ''' 
        Sport.objects.create(user=instance,sport_name=sport)
        UserProfile.objects.create(user=instance,district=district,state=state)
        if license:
            Academy.objects.create(user=instance, license=license)
        return instance 
    

class Academyserializer(ModelSerializer):
    class Meta:
        model = Academy
        fields = ['license','is_certified']
    