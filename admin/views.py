from rest_framework.generics import ListAPIView
from users.models import Users,Sport,UserProfile,Academy
from users.serializers.user_serializer import CustomUsersSerializer,SportSerializer,Academyserializer,UserProfileSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from rest_framework import status

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
            user = Users.objects.get(id= id)
            academy = Academy.objects.get(user=user)
            if value :
                if value == 'approve':
                    academy.is_certified = True
                else:
                    academy.is_certified = False
            academy.save()
            print(value,user,academy.is_certified,'toggle',id)
            return Response('hai')
        except Exception as e:
            print(e,'toglle error')
            return Response('hello')