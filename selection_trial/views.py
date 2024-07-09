from rest_framework import viewsets
from datetime import date
from .models import Trial, TrialRequirement
from .serializers import TrialSerializer,TrialRequirementSerializer
from common.custom_permission_classes import IsAcademy,IsPlayer,IsUser


class TrialViewSet(viewsets.ModelViewSet):
    queryset = Trial.objects.all() 
    serializer_class = TrialSerializer
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user
        if user.is_academy:
            return Trial.objects.filter(academy = user).order_by('-trial_date')
        today = date.today()
        return Trial.objects.filter(trial_date__gte=today).select_related('academy').order_by('trial_date')
    
 

    def retrieve(self, request, *args, **kwargs):
        print(request.data, args,kwargs)
        return super().retrieve(request, *args, **kwargs)