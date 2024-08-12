from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from users.models import Academy, Sport, UserProfile, Users


class SportSerializer(ModelSerializer):
    class Meta:
        model = Sport
        fields = ["sport_name"]


class CustomUsersSerializer(ModelSerializer):
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
    class Meta:
        model = UserProfile
        fields = ["bio", "state", "district", "about", "profile_photo", "cover_photo"]


class Academyserializer(ModelSerializer):
    class Meta:
        model = Academy
        fields = ["license", "is_certified"]
