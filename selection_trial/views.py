from rest_framework import viewsets,views,response,status
from datetime import date
from .models import Trial, TrialRequirement,PlayersInTrial,PlayersInTrialDetails
from .serializers import TrialSerializer,PlayersInTrialSerializer
from common.custom_permission_classes import IsAcademy,IsPlayer,IsUser


class TrialViewSet(viewsets.ModelViewSet):
    queryset = Trial.objects.all() 
    serializer_class = TrialSerializer
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user
        if user.is_academy:
            return Trial.objects.filter(academy = user,is_active=True).order_by('-trial_date')
        today = date.today()
        return Trial.objects.filter(trial_date__gte=today,is_active=True).select_related('academy').order_by('trial_date')

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

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


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