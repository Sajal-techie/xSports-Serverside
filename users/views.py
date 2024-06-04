from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import authenticate,login 
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from users.serializers.user_serializer import CustomUsersSerializer
from .models import Users,UserProfile,Sport,Academy

class Signup(APIView):
    def post(self, request):
        data = request.data
        email = data['email']
        is_academy =True if data['is_academy'] == 'true' else False
        print(email,is_academy,'\n',data)
        if is_academy:
            license = data['license'] 
            print(license,'license')
        state = data['state'] 
        district = data['district']
        sport_name = data['sport_name']
        print(state,sport_name)

        if Users.objects.filter(email=email).exists():
            return Response({
                'status': status.HTTP_400_BAD_REQUEST, 
               'message': 'Email Already Exists'
            })
        serializer = CustomUsersSerializer(data=request.data)
        # print(serializer)
        try:
            serializer.is_valid(raise_exception=True)
            print('000000',serializer.validated_data,'11111111111') 
            serializer.save() 
            user = Users.objects.get(email=email)
            UserProfile.objects.create(user=user,state=state,district=district)
            Sport.objects.create(user=user,sport_name=sport_name)
            return Response({
                'status': status.HTTP_200_OK,
                'message': 'Registration Successful, Check Email For Verification',
                
                }) 
        except Exception as e:
            print(e,'error',serializer.errors,'dafdfasdffsdadsf')
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


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
    