from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import authenticate,login 
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from users.serializers.user_serializer import CustomUsersSerializer
from .models import Users

class Signup(APIView):
    def post(self, request):
        data = request.data
        email = data['email']
        if Users.objects.filter(email=email).exists():
            return Response({
                'status': status.HTTP_400_BAD_REQUEST,
               'message': 'Email Already Exists'
            })
        serializer = CustomUsersSerializer(data=data)
        print(serializer)
        try:
            serializer.is_valid(raise_exception=True)
            print('000000',serializer.validated_data,'11111111111') 
            serializer.save() 
            return Response({
                'status': status.HTTP_200_OK,
                'message': 'Registration Successful, Check Email For Verification',
                
                })
        except Exception as e:
            print(e,'error',serializer.errors,'dafdfasdffsdadsf')
            return Response(serializer.errors)


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
        if 'academy' in data:
            is_academy = True
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
        if user.is_staff or user.is_superuser:
            return Response({
                'status':status.HTTP_400_BAD_REQUEST,
                'message':'Admin cannot loggin as user '
            })
        if not user.is_active:
            return Response({
                'status':status.HTTP_400_BAD_REQUEST,
                'message':'You are blocked'
            })
        if not user.is_verified:
            return Response({
                'status' :status.HTTP_400_BAD_REQUEST,
                'message':'User is not verified'
            })
        if user.is_academy and not is_academy:
            return Response({
                'status':status.HTTP_400_BAD_REQUEST,
                'message': 'You are signed in as acadmey try academy login'
            })
        return Response({
            'status': status.HTTP_200_OK,
           'message': 'Login Successful',
           'user':user.username,
           'role':'player'
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