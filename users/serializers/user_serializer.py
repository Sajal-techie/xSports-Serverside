from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from users.models import Academy, Sport, UserProfile, Users


class SportSerializer(ModelSerializer):
    """
    Serializer for the Sport model.

    Attributes:
        sport_name (str): Name of the sport.
    """
    class Meta:
        model = Sport
        fields = ["sport_name"]


class CustomUsersSerializer(ModelSerializer):
    """
    Serializer for the Users model with additional fields and nested serializers.

    Attributes:
        sport (ListField): List of sport names associated with the user.
        district (str): User's district.
        state (str): User's state.
        license (FileField): Academy license file.
        friends (PrimaryKeyRelatedField): List of user IDs representing friends.
    """
    sport = serializers.ListField(
        child=serializers.CharField(max_length=255), required=False
    )
    district = serializers.CharField(max_length=255, required=False)
    state = serializers.CharField(max_length=255, required=False)
    license = serializers.FileField(required=False)
    friends = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Users.objects.all(), required=False
    )

    class Meta:
        model = Users
        fields = [
            "username",
            "email",
            "phone",
            "dob",
            "is_academy",
            "is_verified",
            "password",
            "sport",
            "district",
            "state",
            "license",
            "id",
            "friends",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        sports = validated_data.pop("sport")
        state = validated_data.pop("state")
        district = validated_data.pop("district")
        license = validated_data.pop("license", None)
        password = validated_data.pop("password")
        instance = super().create(validated_data)
        instance.set_password(password)
        instance.save()
        """create a new instance of sport and userprofile to store sportname 
         district and state """
        for sport in sports:
            Sport.objects.create(user=instance, sport_name=sport)
        UserProfile.objects.create(user=instance, district=district, state=state)
        if license:
            Academy.objects.create(user=instance, license=license)
        return instance


class UserProfileSerializer(ModelSerializer):
    """
    Serializer for the UserProfile model.

    Attributes:
        bio (str): User's bio.
        state (str): User's state.
        district (str): User's district.
        about (str): Additional information about the user.
        profile_photo (ImageField): User's profile photo.
        cover_photo (ImageField): User's cover photo.
    """
    class Meta:
        model = UserProfile
        fields = ["bio", "state", "district", "about", "profile_photo", "cover_photo"]


class Academyserializer(ModelSerializer):
    """
    Serializer for the Academy model.

    Attributes:
        license (FileField): Academy license file.
        is_certified (bool): Indicates if the academy is certified.
    """

    class Meta:
        model = Academy
        fields = ["license", "is_certified"]
