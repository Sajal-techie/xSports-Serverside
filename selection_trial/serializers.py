from real_time.task import send_notification
from rest_framework import serializers
from user_profile.models import Follow
from user_profile.serializers.useracademy_serializer import \
    AcademyDetailSerialiezer

from .models import (PlayersInTrial, PlayersInTrialDetails, Trial,
                     TrialRequirement)


class TrialRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrialRequirement
        fields = ["requirement"]


class TrialSerializer(serializers.ModelSerializer):
    additionalRequirements = serializers.ListField(
        required=False
    )  # to create a new trial using this additional requirement
    additional_requirements = TrialRequirementSerializer(
        many=True, read_only=True
    )  # to pass additional requirement to front end
    academy_details = AcademyDetailSerialiezer(
        source="academy", read_only=True, required=False
    )
    player_count = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        model = Trial
        fields = [
            "id",
            "academy",
            "sport",
            "name",
            "trial_date",
            "trial_time",
            "venue",
            "deadline",
            "is_active",
            "district",
            "state",
            "location",
            "total_participant_limit",
            "registration_fee",
            "description",
            "additionalRequirements",
            "is_participant_limit",
            "is_registration_fee",
            "image",
            "additional_requirements",
            "academy_details",
            "player_count",
        ]

    def create(self, validated_data):
        requirement_data = validated_data.pop("additionalRequirements", [])
        user = self.context["request"].user
        validated_data.pop("is_active", None)
        trial = Trial.objects.create(academy=user, is_active=True, **validated_data)
        for requirement in requirement_data:
            if requirement:
                TrialRequirement.objects.create(trial=trial, requirement=requirement)

        # send notification to all users following this academy
        notification_type = "new_trial"
        text = f"{user.username} added a new Trial"
        link = f"/trial_details/{trial.id}"
        receivers_list = list(
            Follow.objects.filter(academy=user).values_list("player__id", flat=True)
        )

        send_notification.delay(notification_type, text, link, user.id, receivers_list)
        return trial


class PlayersInTrialDetialsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayersInTrialDetails
        fields = ["id", "requirement", "value"]


class PlayersInTrialSerializer(serializers.ModelSerializer):
    additional_requirements = PlayersInTrialDetialsSerializer(
        many=True, required=False, source="playersintrial"
    )

    class Meta:
        model = PlayersInTrial
        fields = [
            "id",
            "player",
            "trial",
            "status",
            "name",
            "dob",
            "number",
            "email",
            "payment_status",
            "state",
            "district",
            "unique_id",
            "achievement",
            "additional_requirements",
            "trial",
        ]

    def validate(self, attrs):
        #  return error if player already joined the same trial
        if PlayersInTrial.objects.filter(
            trial=attrs["trial"], player=attrs["player"]
        ).exists():
            raise serializers.ValidationError("Already registered in this trial ")
        return super().validate(attrs)

    def create(self, validated_data):
        additional_requirements = validated_data.pop("playersintrial", [])
        player = PlayersInTrial.objects.create(status="registered", **validated_data)
        for details in additional_requirements:
            PlayersInTrialDetails.objects.create(
                player_trial=player,
                requirement=details["requirement"],
                value=details["value"],
            )

        return player


class TrialHistorySerializer(serializers.ModelSerializer):
    academy_name = serializers.CharField(source="trial.academy.username")
    trial_id = serializers.IntegerField(source="trial.id")
    trial_name = serializers.CharField(source="trial.name")
    trial_sport = serializers.CharField(source="trial.sport")
    trial_date = serializers.DateField(source="trial.trial_date")
    trial_time = serializers.TimeField(source="trial.trial_time")
    trial_location = serializers.CharField(source="trial.location")
    trial_venue = serializers.CharField(source="trial.venue")
    trial_state = serializers.CharField(source="trial.state")
    trial_district = serializers.CharField(source="trial.district")
    trial_registration_fee = serializers.IntegerField(source="trial.registration_fee")
    trial_description = serializers.CharField(source="trial.description")
    trial_image = serializers.ImageField(source="trial.image")

    class Meta:
        model = PlayersInTrial
        fields = [
            "trial_name",
            "trial_sport",
            "trial_date",
            "trial_time",
            "academy_name",
            "trial_location",
            "trial_venue",
            "trial_state",
            "trial_district",
            "trial_registration_fee",
            "trial_description",
            "trial_image",
            "trial_id",
            "status",
            "name",
            "unique_id",
            "number",
            "email",
        ]
