from django.shortcuts import render
from rest_framework import viewsets,views
from rest_framework import status, generics
from rest_framework.response import Response
import os
from users.models import UserProfile,Sport,Academy,Users
from users.serializers.user_serializer import CustomUsersSerializer,UserProfileSerializer,SportSerializer
from .serializers.useracademy_serializer import UserAcademySerializer
from .serializers.about_serializer import AboutSerializer
from .serializers.achievement_serializer import AchievementSerializer
from .models import UserAcademy,Achievements

class ProfileData(views.APIView):
    # to get all data of a user from different tables 
    def get(self,request): 
        try:
            user = request.user
            profile = UserProfile.objects.get(user=user) if UserProfile.objects.filter(user=user).exists() else None
            sports = Sport.objects.filter(user = user)
            sport_data = []
            for sport in sports:
                sport_data.append(SportSerializer(sport).data)
            print(sport_data,'HAI')
            user_data = {
                'user' : CustomUsersSerializer(user).data,  # it will contain datas in Users model
                'profile': UserProfileSerializer(profile).data,   # it will contain data from UserProfile model
                'sport' : sport_data,   # it will contain data from Sport model
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
        
    def post(self,request):
        try:
            if isinstance(request.user,Users):
                instance = request.user
                print(instance,request.data)
                instance = request.user 
                if 'phone' in request.data:
                    instance.phone = request.data['phone']
                if 'username' in request.data:
                    instance.username = request.data['username']
                if UserProfile.objects.filter(user=instance).exists():
                    profile = UserProfile.objects.get(user=instance)
                else:
                    profile = UserProfile.objects.create(user=instance)
                # sports = Sport.objects.filter(user=instance)
                if 'state' in request.data:
                    profile.state = request.data['state']
                if 'district' in request.data:
                    profile.district = request.data['district']
                if 'bio' in request.data:
                    profile.bio = request.data['bio']
                if 'dob' in request.data:
                    instance.dob = request.data['dob']
                if 'sport' in request.data:
                    Sport.objects.filter(user=instance).exclude(sport_name__in=[request.data['sport']]).delete()
                    for sport in request.data['sport']:
                        print(sport)
                        if not Sport.objects.filter(user=instance,sport_name=sport).exists():
                            Sport.objects.create(user=instance,sport_name = sport)
                
                instance.save()
                profile.save()
                return Response({
                    'status':status.HTTP_200_OK,
                    'message':'User details updated successfully'
                })
            else:
                return Response({
                    'status':status.HTTP_400_BAD_REQUEST,
                    'message':'service not available'
                })
        except Exception as e:
            print(e)
            return Response({
                'status':status.HTTP_400_BAD_REQUEST,
                'message':'some error'
            })


class UpdatePhoto(views.APIView):
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
class UpdateAbout(generics.UpdateAPIView):
    serializer_class = AboutSerializer
    def get_object(self):
        return UserProfile.objects.get(user=self.request.user)


# CRUD academies of players
class UserAcademyManage(viewsets.ModelViewSet):
    serializer_class = UserAcademySerializer
    lookup_field = 'id'
    

    def get_queryset(self):
        return UserAcademy.objects.filter(user=self.request.user).select_related('academy').order_by('-id')


class AchievementManage(viewsets.ModelViewSet):
    serializer_class = AchievementSerializer
    lookup_field = 'id'

    def get_queryset(self):
        return Achievements.objects.filter(user=self.request.user).order_by('-id')