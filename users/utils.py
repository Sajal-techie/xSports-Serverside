from google.auth.transport import requests
from google.oauth2 import id_token
from .models import Users,UserProfile,Sport
from django.contrib.auth import authenticate
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed,PermissionDenied
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class Google():
    @staticmethod 
    def validate(access_token):
        try:   
            id_info = id_token.verify_oauth2_token(access_token,requests.Request(),audience=None,clock_skew_in_seconds=60)
            if "accounts.google.com" in id_info['iss']:
                return id_info
        except Exception as e:
            print(e,'exeprton in validate')
            return "token is invalid or has expired"
    
def login_social_user(email,password):
    user = authenticate(email=email,password=password)
    print(user, 'login with user')
    token_serializer = TokenObtainPairSerializer(data={'email':email,'password':password})
    try:
        if token_serializer.is_valid():
            print('insode toekn')
            access = token_serializer.validated_data.get('access')
            refresh = token_serializer.validated_data.get('refresh')
            return {
                'email':user.email,
                'username':user.username,
                'access':str(access),
                'refresh':str(refresh),
                'dob':user.dob
            }
    except Exception as e:
        print(e)
        raise AuthenticationFailed(
            detail="User not found try signin again"
        )

def register_social_user(provider,email,username):
    user = Users.objects.filter(email=email)
    if user.exists():
        if provider == user[0].auth_provider:
            auth_user = login_social_user(email,settings.SOCIAL_AUTH_PASSWORD)
            return auth_user
        else:
            raise AuthenticationFailed(
                detail=f"please continue login with {user[0].auth_provider}"
            )
    else:
        new_user = {
            'email':email,
            'username':username,
        }
        register_user =Users.objects.create(**new_user)
        register_user.set_password(settings.SOCIAL_AUTH_PASSWORD)
        register_user.auth_provider = provider
        register_user.is_verified = True
        register_user.save()
        print(register_user,'usercreated')
        reg_user = login_social_user(email,settings.SOCIAL_AUTH_PASSWORD)
        UserProfile.objects.create(user=register_user)
        return reg_user