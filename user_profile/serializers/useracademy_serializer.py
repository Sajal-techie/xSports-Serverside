from rest_framework import serializers
from users.models import UserProfile, Users

from ..models import UserAcademy


class AcademyProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the profile photo of an academy.

    This serializer retrieves the profile photo of the academy from the `UserProfile` model.

    Fields:
    - profile_photo: The URL of the academy's profile photo.
    """
    class Meta:
        model = UserProfile
        fields = ["profile_photo"]


class AcademyDetailSerialiezer(serializers.ModelSerializer):
    """
    Serializer for detailed information about an academy.

    This serializer includes the academy's profile photo and username.

    Fields:
    - id: The unique identifier of the academy.
    - username: The username of the academy.
    - profile: The profile details of the academy including profile photo.
    """
    profile = AcademyProfileSerializer(source="userprofile", read_only=True)

    class Meta:
        model = Users
        fields = ["id", "username", "profile"]


class UserAcademySerializer(serializers.ModelSerializer):
    """
    Serializer for the user's academy experience.

    This serializer handles the user's experience with academies, including the 
    details of the academy, the position played, and the duration of the experience.

    Fields:
    - id: The unique identifier for the user's academy experience.
    - academy: The academy the user was associated with.
    - start_month: The month when the user started at the academy.
    - start_year: The year when the user started at the academy.
    - end_month: The month when the user ended at the academy (if applicable).
    - end_year: The year when the user ended at the academy (if applicable).
    - position: The position or role of the user at the academy.
    - is_current: Boolean indicating if the association is still ongoing.
    - sport: The sport associated with the academy experience.
    - academy_details: Detailed information about the academy.
    """
    academy_details = AcademyDetailSerialiezer(
        source="academy", read_only=True, required=False
    )

    class Meta:
        model = UserAcademy
        fields = [
            "id",
            "academy",
            "start_month",
            "start_year",
            "end_month",
            "end_year",
            "position",
            "is_current",
            "sport",
            "academy_details",
        ]

    def validate(self, attrs):
        if "is_current" in attrs:
            if attrs["is_current"]:
                attrs["end_month"] = ""
                attrs["end_year"] = ""
        if "start_month" not in attrs:
            raise serializers.ValidationError({"message": "Enter valid Start Month"})
        elif "start_year" not in attrs:
            raise serializers.ValidationError({"message": "Enter valid start year"})
        elif "sport" not in attrs:
            raise serializers.ValidationError({"message": "Enter valid sport"})
        elif "position" not in attrs:
            raise serializers.ValidationError({"message": "Enter valid position"})
        return attrs

    def validate_academy(self, value):
        if value is None:
            raise serializers.ValidationError({"message": "Enter valid academy"})
        return value

    def create(self, validated_data):
        user = self.context["request"].user
        return UserAcademy.objects.create(user=user, **validated_data)
