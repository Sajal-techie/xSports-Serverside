from rest_framework import viewsets
from .models import Trial, TrialRequirement
from .serializers import TrialSerializer,TrialRequirementSerializer
from common.custom_permission_classes import IsAcademy,IsPlayer,IsUser


class TrialViewSet(viewsets.ModelViewSet):
    queryset = Trial.objects.all() 
    serializer_class = TrialSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_academy:
            return Trial.objects.filter(academy = user).order_by('-trial_date')
        return Trial.objects.all().order_by('-trial_date')
    
    def create(self, request, *args, **kwargs):
        print(request.data)
        return super().create(request, *args, **kwargs)

