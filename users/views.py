from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

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
            return Response({
                'status': status.HTTP_200_OK,
                'message': 'OTP Verified'
            })
        return Response({
            'status': status.HTTP_400_BAD_REQUEST,
            'message': 'Invalid OTP'
        })
