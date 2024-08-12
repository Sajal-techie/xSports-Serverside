from rest_framework.serializers import ModelSerializer
from users.models import UserProfile


class AboutSerializer(ModelSerializer):
    """
    Serializer for the `UserProfile` model to handle 'about' field.

    This serializer is used to serialize and deserialize the 'about' field
    of the `UserProfile` model.

    Fields:
    - about: A text field containing the user's biography or personal information.
    """
    class Meta:
        model = UserProfile
        fields = ["about"]
