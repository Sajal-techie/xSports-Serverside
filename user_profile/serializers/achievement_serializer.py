import os

from rest_framework.serializers import ModelSerializer

from ..models import Achievements


class AchievementSerializer(ModelSerializer):
    """
    Serializer for the `Achievements` model.

    This serializer handles the serialization and deserialization of the
    `Achievements` model, which includes fields related to user achievements.

    Fields:
    - id: The unique identifier for the achievement.
    - title: The title of the achievement.
    - issued_by: The entity that issued the achievement.
    - issued_month: The month when the achievement was issued.
    - issued_year: The year when the achievement was issued.
    - image: An image associated with the achievement.
    - description: A description of the achievement.
    - user: The user associated with the achievement.
    """
    class Meta:
        model = Achievements
        fields = [
            "id",
            "title",
            "issued_by",
            "issued_month",
            "issued_year",
            "image",
            "description",
            "user",
        ]


    def create(self, validated_data):
        """
        Create a new `Achievements` instance.

        Adds the current user (from request context) to the achievement being created.

        Args:
            validated_data (dict): The validated data for creating the achievement.

        Returns:
            Achievements: The newly created `Achievements` instance.
        """
        user = self.context["request"].user
        return Achievements.objects.create(user=user, **validated_data)

    def update(self, instance, validated_data):
        """
        Update an existing `Achievements` instance.

        If the `image` field is being updated and a new image is provided, 
        the old image file is deleted from the filesystem.

        Args:
            instance (Achievements): The existing `Achievements` instance to update.
            validated_data (dict): The validated data for updating the achievement.

        Returns:
            Achievements: The updated `Achievements` instance.
        """
        if instance.image and os.path.exists(instance.image.path):
            os.remove(instance.image.path)
        return super().update(instance, validated_data)
