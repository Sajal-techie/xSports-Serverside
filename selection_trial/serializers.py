from rest_framework import serializers
from .models import Trial,TrialRequirement


class TrialRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrialRequirement
        fields = ['requirement']
    

class TrialSerializer(serializers.ModelSerializer):
    additionalRequirements = serializers.ListField(required=False)  # to create a new trial using this additional requirement
    additional_requirements = TrialRequirementSerializer(many=True, read_only=True) # to pass additional requirement to front end

    class Meta:
        model = Trial
        fields = [
            'id', 'academy', 'sport', 'name', 'trial_date', 'trial_time', 'venue', 'deadline', 
            'district', 'state', 'location','total_participant_limit', 'registration_fee', 'description', 'additionalRequirements',
            'is_participant_limit', 'is_registration_fee', 'image', 'additional_requirements' ,
        ]
    
    def create(self, validated_data):
        print(validated_data,'validated data')
        requirement_data = validated_data.pop('additionalRequirements',[])
        user = self.context['request'].user
        print(user)
        trial = Trial.objects.create(academy=user,**validated_data)
        print(requirement_data,'reqdata',validated_data)
        for requirement in requirement_data:
            if requirement:
                TrialRequirement.objects.create(trial=trial,requirement=requirement ) 
            print(requirement,'requeirement',type(requirement))

        print(trial)
        return trial