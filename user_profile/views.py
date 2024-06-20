from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status, generics
from rest_framework.response import Response
import os
from users.models import UserProfile,Sport,Academy
from users.serializers.user_serializer import CustomUsersSerializer,UserProfileSerializer,SportSerializer
from .profile_serializer import AboutSerializer

class ProfileData(APIView):
    # to get all user data from different tables 
    def get(self,request): 
        try:
            user = request.user
            profile = UserProfile.objects.get(user=user)
            sport = Sport.objects.get(user = user)
            user_data = {
                'user' : CustomUsersSerializer(user).data,  # it will contain datas in Users model
                'profile': UserProfileSerializer(profile).data,   # it will contain data from UserProfile model
                'sport' : SportSerializer(sport).data,   # it will contain data from Sport model
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
    #  to update profile photo or cover photo
    def post(self, request,id):
        try:
            print(request.data,'request data lll')
            user = request.user
            serializer = UserProfileSerializer(user, data=request.data)
            if serializer.is_valid(raise_exception=True):
                profile = UserProfile.objects.get(user=user)
                if serializer.validated_data.get('profile_photo',None):  #check whether data has profile photo or cover photo
                    new_photo = serializer.validated_data.get('profile_photo',None)
                    oldpath = profile.profile_photo.path if (profile.profile_photo and new_photo) else None
                    profile.profile_photo = new_photo   
                    print('profile photo = ',new_photo,oldpath)
                    message = "Profile Photo updated successfully"
                elif serializer.validated_data.get('cover_photo',None):
                    new_photo = serializer.validated_data.get('cover_photo',None)
                    oldpath = profile.cover_photo.path if (profile.cover_photo and new_photo) else None
                    profile.cover_photo = new_photo   
                    print('cover photo = ',new_photo,oldpath)
                    message = "Cover Photo updated successfully"
                else:                                                   # if data does not contain profile or cover return failed
                    print('else case')
                    return Response({
                        'status': status.HTTP_400_BAD_REQUEST,
                        'message':'No valied data updation failed'
                    })
                profile.save()
                serializer.save()  
                if oldpath and os.path.exists(oldpath):
                    print('hai removing old path ')
                    os.remove(oldpath)
                return Response({
                    'status': status.HTTP_200_OK,
                    'message': message
                })
            return Response({
                    'status': status.HTTP_400_BAD_REQUEST,
                    'message': 'photo updation failed '
                })
        except Exception as e:
            print(e,'erro in uplaod image')
            return Response({
                'status':status.HTTP_400_BAD_REQUEST,
                'message': "Photo updation failed",
            })
        
    #  to delete profile photo or cover photo 
    def delete(self,request,id):
        try:
            user = request.user
            data = request.data
            print(data,user,'datas and user')
            profile = UserProfile.objects.get(user=user)
            oldpath = None
            if 'type' in data and data['type'] == 'profile':
                    oldpath = profile.profile_photo.path if profile.profile_photo else None
                    profile.profile_photo = None
                    message = "Profile Photo deleted successfully"
            elif 'type' in data and data['type'] == 'cover':
                    oldpath = profile.cover_photo.path if profile.cover_photo else None
                    profile.cover_photo = None
                    message = "Cover Photo deleted successfully"
            else:
                return Response({
                    'status': status.HTTP_400_BAD_REQUEST,
                    'message':"No valid data photo deletion Failed"
                })
            profile.save()
            if oldpath and os.path.exists(oldpath):
                os.remove(oldpath)
            return Response({
                'status':status.HTTP_200_OK,
                'message':message
            })
        except Exception as e:
            print(e,'error deleting')
            return Response({
                'status':status.HTTP_400_BAD_REQUEST,
                'message':"Photo deletion failed"
            })

# update about of user 
class UpdateAbout(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AboutSerializer
    def get_object(self):
        return UserProfile.objects.get(user=self.request.user)
