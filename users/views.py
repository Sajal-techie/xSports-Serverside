from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import authenticate,login 
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.parsers import MultiPartParser

from users.serializers.user_serializer import CustomUsersSerializer,Academyserializer,UserProfileSerializer,SportSerializer
from .models import Users,UserProfile,Sport,Academy

class Signup(APIView):
    # parser_classes = (MultiPartParser,)
    def post(self, request):
        data = request.data
        email = data['email']
        print(email,'\n',data)


        if Users.objects.filter(email=email).exists():
            return Response({
                'status': status.HTTP_400_BAD_REQUEST, 
               'message': 'Email Already Exists'
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
        # print(userdetail.email,userdetail.password,userdetail.check_password(password))
        # user =  authenticate(request=request,email=email,password=password)
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
        if not user.is_verified :
            return Response({
                'status' :status.HTTP_400_BAD_REQUEST,
                'message':'User is not verified'
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
        
        role = 'admin' if is_staff and user.is_staff else 'academy' if is_academy else 'player'

        return Response({
            'status': status.HTTP_200_OK,
           'message': 'Login Successful',
           'user':user.username,
           'role':role
        })

class Profile(APIView):
    # permission_classes = [IsAuthenticated] 
    # authentication_classes = [JWTAuthentication]
    def get(self,request):
        # user = request.user
        # serializer = CustomUsersSerializer(user)
        return Response({
            'status': status.HTTP_200_OK,
            'data': 'hai hello this is profile'
        })
    