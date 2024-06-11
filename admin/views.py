from django.core.mail import send_mail
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from rest_framework import status
from django.conf import settings
from users.serializers.user_serializer import CustomUsersSerializer,SportSerializer,Academyserializer,UserProfileSerializer
from users.models import Users,Sport,UserProfile,Academy

class AcademyManage(APIView):
    def get(self, request):
        users = Users.objects.filter(is_academy=True).order_by('-id')
        user_data = []
        for user in users:
            print(user.username,user.id)
            if UserProfile.objects.filter(user=user).exists():
                user_profile = UserProfile.objects.get(user=user)
            if Sport.objects.filter(user=user).exists():
                sport = Sport.objects.get(user=user)
            if Academy.objects.filter(user=user).exists():
                academy_data = Academy.objects.get(user=user)
            user_data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'dob':user.dob,
                'profile': UserProfileSerializer(user_profile).data,
                'sport': SportSerializer(sport).data,
                'academy_data': Academyserializer(academy_data).data,
            })
        if not user_data:
            return Response({
                'academy': user_data,
                'status':status.HTTP_204_NO_CONTENT
            })
        return Response({
                        'academy':user_data,
                        'status': status.HTTP_200_OK
                        })
        

class ToggleIsCertified(APIView):
    def post(self,request,id,):
        try:
            value = request.data.get('value',None)
            user = Users.objects.get(id=id)
            academy = Academy.objects.get(user=user)
            if value :
                if value == 'approve':
                    subject = "Your account has Approved by Admin"
                    message = f" Now you can login http://localhost:5173/"
                    academy.is_certified = True
                else:
                    subject = "Your account has been Denied by admin"
                    message = f"Your playMaker account with email {user.email} has been denied by admin"
                    academy.is_certified = False
                email_from = settings.EMAIL_HOST_USER
                send_mail(subject,message,email_from,[user.email])
            academy.save()
            print(value,user,academy.is_certified,'toggle',id)
            return Response({
                'status': status.HTTP_200_OK,
                'message':"Certification updated successfully"
            })
        except Exception as e:
            print(e,'toglle error')
            return Response({
                'status': status.HTTP_400_BAD_REQUEST,
                'message':"some error"
            })
    

class PlayerManage(APIView):
    def get(self, request):
        players = Users.objects.filter(Q (is_academy=False) & Q(is_staff=False) & Q(is_superuser=False)).order_by('-id')
        player_data = []
        for user in players:
            print(user.username,user.id)
            if UserProfile.objects.filter(user=user).exists():
                user_profile = UserProfile.objects.get(user=user)
            if Sport.objects.filter(user=user).exists():
                sport = Sport.objects.get(user=user)
            player_data.append({
                'id':user.id,
                'username': user.username,
                'email': user.email,
                'dob':user.dob,
                'is_active':user.is_active,
                'profile': UserProfileSerializer(user_profile).data,
                'sport':SportSerializer(sport).data,
            })
        if not player_data: 
            return Response({
                'player': player_data,
                'status': status.HTTP_204_NO_CONTENT
            })
    
        return Response({
            'player': player_data,
            'status': status.HTTP_200_OK
        })


class ToggleActive(APIView):
    def post(self, request, id):
        print('never say never')
        try:
            value = request.data.get('value',None)
            print(value,'balue')
            user = Users.objects.get(id=id)
            if value:
                if value == 'active':
                    user.is_active = True
                    user.save()
                else:
                    user.is_active = False
                    user.save()
                
            return Response({
                'status': status.HTTP_200_OK,
                'message': "Updated successfully"
            })
        except Exception as e:
            return Response({
                'status':status.HTTP_400_BAD_REQUEST,
                'message': "Updation failed"
            })
            