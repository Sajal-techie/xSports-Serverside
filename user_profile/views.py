from django.shortcuts import render
from rest_framework import viewsets,views,status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
import os
from django.core.cache import cache
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from users.models import UserProfile,Sport,Academy,Users
from users.serializers.user_serializer import CustomUsersSerializer,UserProfileSerializer,SportSerializer
from .serializers.useracademy_serializer import UserAcademySerializer
from .serializers.about_serializer import AboutSerializer
from .serializers.achievement_serializer import AchievementSerializer
from .serializers.connection_serializer import FriendRequestSerializer,FollowSerializer,FriendListSerializer
from .models import UserAcademy,Achievements,FriendRequest,Follow
from common.custom_permission_classes import IsPlayer,IsAcademy,IsUser,IsAdmin 

class ProfileData(views.APIView):
    permission_classes = [IsUser,IsAuthenticated]
    # to get all data of a user from different tables 
    def get(self,request): 
        try:
            user = request.user
            cache_key = f"profile_{user.id}"
            user_data = cache.get(cache_key)
            print(user_data,'cached user data')
            if not user_data:
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
                cache.set(cache_key,user_data,timeout=60*15) # adding data to cache
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
                cache_key = f"profile_{instance.id}"
                cache.delete(cache_key)  # deleting cached data after updating
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
    permission_classes = [IsUser,IsAuthenticated]

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
                else:                                                  # if data does not contain profile or cover return failed
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
                
                cache_key = f"profile_{user.id}"
                cache.delete(cache_key)  # deleting cached data 
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

            cache_key = f"profile_{user.id}"
            cache.delete(cache_key)
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
    permission_classes = [IsUser,IsAuthenticated]
    serializer_class = AboutSerializer


    def get_object(self):
        return UserProfile.objects.get(user=self.request.user)


    def perform_update(self, serializer):
        cache_key = f"profile_{self.request.user.id}"
        cache.delete(cache_key)
        return super().perform_update(serializer)


# CRUD academies of players
class UserAcademyManage(viewsets.ModelViewSet):
    permission_classes = [IsPlayer,IsAuthenticated]
    serializer_class = UserAcademySerializer
    lookup_field = 'id'
    

    def get_queryset(self):
        return UserAcademy.objects.filter(user=self.request.user).select_related('academy').order_by('-id')


class AchievementManage(viewsets.ModelViewSet):
    permission_classes = [IsUser,IsAuthenticated]
    serializer_class = AchievementSerializer
    lookup_field = 'id'

    def get_queryset(self):
        return Achievements.objects.filter(user=self.request.user).order_by('-id')
    

class FriendRequestViewSet(viewsets.ModelViewSet):
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer
    
    def get_queryset(self):
        return FriendRequest.objects.filter(to_user=self.request.user).select_related('to_user') 

    @action(detail=True, methods=['get'])
    def sent_request_list(self,*args, **kwargs):
        sent_requests =  FriendRequest.objects.filter(from_user=self.request.user).select_related('from_user')
        serializer = self.get_serializer(sent_requests)
        return Response(serializer.data,status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        print(request.data,request.user,args,kwargs)
        data = request.data
        from_user = request.user
        to_user = Users.objects.get(id=data['to_user'])

        if from_user == to_user:
            return Response({'message':"You can't send friend request to yourself"},status=status.HTTP_400_BAD_REQUEST)

        if FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
            return Response({'message':'Friend Request already sent..'},status=status.HTTP_400_BAD_REQUEST)
        
        friend_request = FriendRequest.objects.create(from_user=from_user, to_user=to_user)
        serializer = self.get_serializer(friend_request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

    @action(detail=True, methods=['post'])
    def accept_request(self, request, pk=None):
        print(pk,request.user,'unios')
        friend_request = FriendRequest.objects.get(from_user=pk,to_user=request.user)
        friend_request.accept()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['post'])
    def reject_request(self, request, pk=None):
        friend_request = FriendRequest.objects.get(from_user=pk,to_user=request.user)
        print(friend_request)
        friend_request.reject()
        return Response(status=status.HTTP_204_NO_CONTENT)
        

class FriendViewSet(viewsets.ModelViewSet):
    serializer_class = FriendListSerializer

    def get_queryset(self):
        user = self.request.user
        return user.friends.all().select_related('userprofile').prefetch_related('sport_set')


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer

    def create(self,request, *args, **kwargs):
        data = request.data
        print(data)
        player = request.user
        academy_id = data['academy']
        academy = Users.objects.get(id=academy_id)

        if Follow.objects.filter(player=player, academy=academy).exists():
            return Response({'message':'Already following this academy'}, status=status.HTTP_400_BAD_REQUEST)
        
        follow = Follow.objects.create(player=player,academy=academy)
        serializer = FollowSerializer(follow)
        return Response(serializer.data,status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def unfollow(self, request):
        player = request.user
        academy_id = request.data.get('academy_id', None)
        if not academy_id:
            return Response({'message':"academy id is required"},status=status.HTTP_400_BAD_REQUEST)
        
        follow = Follow.objects.filter(player=player,academy=academy_id).first()
        if follow:
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'message':'You are not following this academy'},status=status.HTTP_400_BAD_REQUEST)
    

