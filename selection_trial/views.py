from rest_framework import viewsets,views,response,status
from rest_framework.decorators import action
from datetime import date
from django.db.models import Count
from .models import Trial, TrialRequirement,PlayersInTrial,PlayersInTrialDetails
from .serializers import TrialSerializer,PlayersInTrialSerializer
from common.custom_permission_classes import IsAcademy,IsPlayer,IsUser,IsAdmin
from .tasks import send_status_mail

class TrialViewSet(viewsets.ModelViewSet):
    queryset = Trial.objects.all() 
    serializer_class = TrialSerializer
    lookup_field = 'id'
    permission_classes = [IsUser]

    def get_queryset(self):
        user = self.request.user
        if user.is_academy:
            return Trial.objects.filter(academy = user,is_active=True).annotate(player_count=Count('trial')).order_by('-trial_date')
        today = date.today()
        return Trial.objects.filter(trial_date__gte=today,is_active=True).annotate(player_count=Count('trial')).select_related('academy').order_by('trial_date')

    def retrieve(self, request, *args, **kwargs):
        print(request.data, args,kwargs)
        return super().retrieve(request, *args, **kwargs)
    
    def destroy(self, request,id, *args, **kwargs):
        print(self,request,args, kwargs,id) 
        trial = Trial.objects.get(id=id)
        trial.is_active = False
        trial.save()
        return response.Response(status=status.HTTP_200_OK)

class PlayersInTrialViewSet(viewsets.ModelViewSet):
    queryset = PlayersInTrial.objects.all()
    serializer_class = PlayersInTrialSerializer
    lookup_field = 'id'
    permission_classes = [IsUser]

    def list_players_in_trial(self,request,trial_id=None):
        print(trial_id,request,request.data)
        players = self.queryset.filter(trial=trial_id).prefetch_related('playersintrial').order_by('id')
        serialzer = self.get_serializer(players,many=True)
        print(serialzer.data)
        return response.Response(serialzer.data,status=status.HTTP_200_OK)

    def partial_update(self, request,id, *args, **kwargs):
        print(request,request.data,args, kwargs,id)
        player = PlayersInTrial.objects.get(id=id)
        print(player)
        if request.data['status'] == 'selected':    
            message = f"""We are excited to inform you that  you are selected in the 
                        {player.trial.name}'s conducted by {player.trial.academy.username} academy ,
                        further information will be provided please stay tuned"""
        else:
            message = f"""We are sorry to inform that  you are not seleted in the 
                        {player.trial.name}'s conducted by {player.trial.academy.username} academy , 
                        Thank you for you participation . """
        send_status_mail.delay(email=player.email,trial_name=player.trial.name,message=message)
        return super().partial_update(request, *args, **kwargs)
    

class PlayerExistInTrialView(views.APIView):
    def get(self,request,id,*args, **kwargs):
        user = request.user
        total_count = PlayersInTrial.objects.filter(trial=id).count() 
        if PlayersInTrial.objects.filter(player=user,trial=id).exists():
            print('hai',id,*args, **kwargs)
            player_trial = PlayersInTrial.objects.get(player=user,trial=id)
            print(player_trial.status,player_trial.unique_id,total_count)
            return response.Response(data={
                'status':player_trial.status,
                'unique_id':player_trial.unique_id,
                'count':total_count
            },status=status.HTTP_200_OK)
        else:
            print(total_count)
            return response.Response(data={'count':total_count},status=status.HTTP_206_PARTIAL_CONTENT) 