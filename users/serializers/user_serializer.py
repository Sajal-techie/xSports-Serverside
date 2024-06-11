from rest_framework.serializers import ModelSerializer,Serializer
from rest_framework import serializers
from users.models import Users,Sport,UserProfile,Academy
import random
from django.core.mail import send_mail
from django.conf import settings


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
    # sports = SportSerializer(read_only =True)
    # user_profile= UserProfileSerializer(read_only=True)

    class Meta: 
        model = Users  
        fields = [
            'username', 'email', 'phone', 'dob', 'is_academy',
             'is_verified', 'password','sport','district','state','license'
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
        send_otp(instance.email) 
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


def send_otp(email):
    try:
        print('in send amil')
        subject = 'Your verification email'
        otp = random.randint(100000, 999999)
        message = f'your otp is {otp}'
        email_from = settings.EMAIL_HOST_USER
        user = Users.objects.get(email=email)
        user.otp = otp
        user.save()
        print(user.otp,otp, user.username, 'in send otp function')
        send_mail(subject, message, email_from,[email])
    except Exception as e:
        # Handle exceptions (e.g., email sending failure or user retrieval failure)
        print(f"Error sending OTP: {e}")