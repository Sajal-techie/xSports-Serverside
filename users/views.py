from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import authenticate,login 
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.parsers import MultiPartParser
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.validators import validate_email
from users.serializers.user_serializer import CustomUsersSerializer,Academyserializer,UserProfileSerializer,SportSerializer
from .models import Users,UserProfile,Sport,Academy
from users.serializers.user_serializer import send_otp 

class Signup(APIView):
    # parser_classes = (MultiPartParser,)
    def post(self, request):
        data = request.data
        
        # validations 
        errors = {}
        print('username' in data)
        if 'email' in data:
            if not data['email'] :
                print('hai hello')
                errors['email'] = "Email field is Required"
        else :
            try:
                validate_email(email)
            except:
                errors['email'] = "Email is not Valid"
       
        email = data['email']
        print(email,'\n',data)

        if 'username' in data:
            if not data['username']:
                errors['username'] = "Name is required"
        if 'sport' in data:
            if not data['sport']:
                errors['sport'] = "Sport is Required"
        if 'state' in data:
            if not data['state']:
                errors['state'] = "State is required"
        if 'district' in data:
            if not data['district']:
                errors['district'] = "District is required"
        if 'dob' in data:
            if not data['dob']:
                errors['dob'] = "Date of birth is required"
        if 'password' in data:
            if not data['password']:
                errors['password'] = "Password is required"
        if 'license' in data:
            if not data['license']:
                errors['license'] = "License is required"

        print(errors,'errors')
        if Users.objects.filter(email=email).exists():
            errors['email'] = "Email already exists"

        if errors:
            return Response({
                'status':status.HTTP_400_BAD_REQUEST,
                'message' : errors.values()
            })
        user_serializer = CustomUsersSerializer(data=data)
        try:
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save() 
            return Response({
                'status': status.HTTP_200_OK,
                'message': 'Registration Successful, Check Email For Verification',
                
                })  
        except Exception as e:
            print(e,'exeption errorrrrr')
            return Response(e,status=status.HTTP_400_BAD_REQUEST)
 

class VerifyOtp(APIView):
    def put(self, request):
        data = request.data
        email = data['email']
        otp = data['otp']
        user = Users.objects.get(email=email)
        print(data,otp,email,user.otp)
        if user.otp == otp:
            user.otp = None
            user.is_verified = True
            user.save()
            return Response({
                'status': status.HTTP_200_OK,
                'message': 'OTP Verified'
            })
        return Response({
            'status': status.HTTP_400_BAD_REQUEST,
            'message': 'Invalid OTP'
        }) 

class Login(APIView):
    def post(self, request): 
        data = request.data
        email = data['email']
        password = data['password']
        is_academy = data['is_academy'] 
        is_staff = True if 'is_staff' in data else False
        print(data,is_academy,is_staff)
        if not Users.objects.filter(email=email).exists():
            return Response({
                'status': status.HTTP_400_BAD_REQUEST,
               'message': 'Email Does Not Exists'
            })
        user = Users.objects.get(email = email)
        print(user)
        if not user.check_password(password):
            return Response({
                'status': status.HTTP_400_BAD_REQUEST,
               'message': 'Invalid Password'
            })
        if user.is_superuser or (user.is_staff and not is_staff):
            return Response({
                'status':status.HTTP_400_BAD_REQUEST,
                'message':'Admin cannot loggin as user'
            })
        if is_staff and not user.is_staff:
            return Response({
                'status':status.HTTP_400_BAD_REQUEST,
                'message':'You are not an admin '
            })
        if not user.is_active:
            return Response({
                'status':status.HTTP_400_BAD_REQUEST, 
                'message':'You are blocked'
            })
        if user.is_academy and not is_academy:
            return Response({
                'status':status.HTTP_400_BAD_REQUEST,
                'message': 'You are signed in as acadmey try academy login'
            })
        if not user.is_academy and is_academy:
            return Response({
                'status':status.HTTP_400_BAD_REQUEST,
                'message': 'You are signed in as player try player login'
            })
        if not user.is_verified:
            send_otp(email=user.email)
            return Response({
                'status' :status.HTTP_403_FORBIDDEN,
                'message':'User is not verified'
            })
        if is_academy:
            academy = Academy.objects.get(user=user)
            if not academy.is_certified :
                return Response({
                    'status':status.HTTP_400_BAD_REQUEST,
                    'message':'You are not approved by admin '
                })

        role = 'admin' if is_staff and user.is_staff else 'academy' if is_academy else 'player'

        return Response({
            'status': status.HTTP_200_OK,
           'message': 'Login Successful',
           'user':user.username,
           'role':role
        })

class Logout(APIView):
    
    def post(self, request):
        print(request.user,'suser')
        try:
            refresh = request.data.get('refresh')
            print(refresh,'refresh in logout',request.data)
            token = RefreshToken(refresh)
            print(token,'token in logout')
            token.blacklist()
            return Response(status=200)
        except Exception as e:
            print(e,'error in logout')
            return Response(status=400)

class Profile(APIView):
    # permission_classes = [IsAuthenticated] 
    # authentication_classes = [JWTAuthentication]

    def get(self,request): 
        user = request.user
        print(user,'user')
        print(user.email,' email')
        profile = UserProfile.objects.get(user=user)
        print(UserProfileSerializer(profile).data,'profile data serialzed')
        sport = Sport.objects.get(user = user)
        user_data = {
            'user' : CustomUsersSerializer(user).data,
            'profile': UserProfileSerializer(profile).data,
            'sport' : SportSerializer(sport).data,
        }
        return Response({
            'status': status.HTTP_200_OK,
            'user_details': user_data
        })


class ResendOtp(APIView):
    def post(self,request):
        try:

            print(request.data)
            email = request.data['email']
            send_otp(email)
            return Response({
                'status':status.HTTP_200_OK,
                'message':"OTP sended successfully"
            })
        except Exception as e:
            return Response({
                'status':status.HTTP_400_BAD_REQUEST,
                'message': 'Error sending otp'
            })