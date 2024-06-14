from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.views.generic.edit import UpdateView
import os
from users.models import UserProfile,Sport,Academy
from users.serializers.user_serializer import CustomUsersSerializer,UserProfileSerializer,SportSerializer
from .profile_serializer import ImageSerializer

#  to get the user data to show in the profile page 
class ProfileData(APIView):
    # permission_classes = [IsAuthenticated] 
    # authentication_classes = [JWTAuthentication]

    def get(self,request): 
        try:
            user = request.user
            profile = UserProfile.objects.get(user=user)
            sport = Sport.objects.get(user = user)
            user_data = {
                'user' : CustomUsersSerializer(user).data, # it will contain datas in Users model
                'profile': UserProfileSerializer(profile).data, # it will contain data from UserProfile model
                'sport' : SportSerializer(sport).data, # it will contain data from Sport model
            }
            return Response({
                'status': status.HTTP_200_OK,
                'user_details': user_data
            })
        except Exception as e:
            print(e,'error in getting userdata')
            return Response({
                'status': status.HTTP_400_BAD_REQUEST,
                'message': "server error"
            })





class UpdatePhoto(APIView):
    # model = UserProfile
    # fields = ['profile_photo']
    def post(self, request,id):
        try:
            print(request.data,'request data lll')
            user = request.user
            serializer = UserProfileSerializer(user, data=request.data)
            if serializer.is_valid(raise_exception=True):
                profile = UserProfile.objects.get(user=user)
                new_photo = serializer.validated_data.get('profile_photo',None)
                oldpath = profile.profile_photo.path if (profile.profile_photo and new_photo)  else None
                profile.profile_photo = new_photo
                profile.save()
                serializer.save()  
                print('saved',oldpath) 
                if oldpath and os.path.exists(oldpath):
                    print('hai removing old path ')
                    os.remove(oldpath)
                return Response({
                    'status': status.HTTP_200_OK,
                    'message': 'profile photo updated successfully'
                })
            return Response({
                    'status': status.HTTP_400_BAD_REQUEST,
                    'message': 'profile photo updation failed '
                })
        except Exception as e:
            print(e,'erro in uplaod image')
            return Response({
                'status':status.HTTP_400_BAD_REQUEST,
                'message': "Some error"
            })
    def delete(self,request,id):
        try:
            user = request.user
            data = request.data
            print(data,user,'datas and user')
            profile = UserProfile.objects.get(user=user)
            oldpath = profile.profile_photo.path if profile.profile_photo else None
            profile.profile_photo = None
            profile.save()
            if oldpath and os.path.exists(oldpath):
                os.remove(oldpath)
            return Response({
                'status':status.HTTP_200_OK,
                'message':'Photo deleted successfully'
            })
        except Exception as e:
            print(e,'error deleting')
            return Response({
                'status':status.HTTP_400_BAD_REQUEST,
                'message':"photo deletion failed"
            })