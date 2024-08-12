from rest_framework.serializers import ModelSerializer
from ..models import Achievements
import os


class AchievementSerializer(ModelSerializer):
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
        user = self.context["request"].user
        return Achievements.objects.create(user=user, **validated_data)

    def update(self, instance, validated_data):
        if instance.image and os.path.exists(instance.image.path):
            os.remove(instance.image.path)
        return super().update(instance, validated_data)
