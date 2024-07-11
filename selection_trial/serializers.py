from rest_framework import serializers
from .models import Trial,TrialRequirement,PlayersInTrial,PlayersInTrialDetails
from user_profile.serializers.useracademy_serializer import AcademyDetailSerialiezer 

class TrialRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrialRequirement
        fields = ['requirement']
    

class TrialSerializer(serializers.ModelSerializer):
    additionalRequirements = serializers.ListField(required=False)  # to create a new trial using this additional requirement
    additional_requirements = TrialRequirementSerializer(many=True, read_only=True) # to pass additional requirement to front end
    academy_details = AcademyDetailSerialiezer(source='academy',read_only=True,required=False)
    
    class Meta:
        model = Trial
        fields = [
            'id', 'academy', 'sport', 'name', 'trial_date', 'trial_time', 'venue', 'deadline', 
            'district', 'state', 'location','total_participant_limit', 'registration_fee', 'description', 'additionalRequirements',
            'is_participant_limit', 'is_registration_fee', 'image', 'additional_requirements' ,'academy_details'
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


class PlayersInTrialDetialsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayersInTrialDetails
        fields = ['id','requirement','value']


class PlayersInTrialSerializer(serializers.ModelSerializer):
    additional_requirements = PlayersInTrialDetialsSerializer(many=True,required=False)
    class Meta:
        model = PlayersInTrial
        fields = [
            'id', 'player', 'trial', 'status', 'name', 'dob', 'number', 'email', 
            'state', 'district', 'unique_id', 'achievement','additional_requirements'
        ]

    def create(self, validated_data):
        additional_requirements = validated_data.pop('additional_requirements',{})
        print(validated_data,'validated data',additional_requirements)
        player = PlayersInTrial.objects.create(status='registered',**validated_data)
        for details in additional_requirements:
            print(details,details['requirement'])
            PlayersInTrialDetails.objects.create(player_trial = player,requirement=details['requirement'],value=details['value'])
        
        return player