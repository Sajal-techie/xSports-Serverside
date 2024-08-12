from django.contrib.auth import get_user_model
from rest_framework import serializers
from ..models import Follow, FriendRequest

User = get_user_model()


class FriendListSerializer(serializers.ModelSerializer):
    """
    Serializer for user profiles in the friend list.

    This serializer provides the basic details of users including profile photo
    and bio, for use in friend lists and related functionalities.

    Fields:
    - id: The unique identifier for the user.
    - username: The username of the user.
    - is_academy: Boolean indicating if the user is an academy.
    - profile_photo: The URL of the user's profile photo.
    - bio: The user's biography.
    """
    profile_photo = serializers.SerializerMethodField("get_profile_photo")
    bio = serializers.SerializerMethodField("get_bio")

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "is_academy",
            "profile_photo",
            "bio",
        ]

    def get_profile_photo(self, obj):
        """
        Retrieve the URL of the user's profile photo.

        Checks if the user has a related `UserProfile` and if it has a profile photo.

        Args:
            obj (User): The user instance.

        Returns:
            str or None: URL of the profile photo or None if not available.
        """
        if hasattr(obj, "userprofile") and obj.userprofile.profile_photo:
            return obj.userprofile.profile_photo.url
        return None

    def get_bio(self, obj):
        """
        Retrieve the user's biography.

        Checks if the user has a related `UserProfile` and if it has a bio.

        Args:
            obj (User): The user instance.

        Returns:
            str or None: User's bio or None if not available.
        """
        if hasattr(obj, "userprofile") and obj.userprofile.bio:
            return obj.userprofile.bio
        return None


class FriendRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for friend requests between users.

    This serializer provides details about friend requests, including information
    about the users involved.

    Fields:
    - id: The unique identifier for the friend request.
    - from_user: The user who sent the friend request.
    - to_user: The user who received the friend request.
    - status: The status of the friend request (e.g., pending, accepted).
    - created_at: The timestamp when the friend request was created.
    """
    from_user = FriendListSerializer(read_only=True)
    to_user = FriendListSerializer(required=False)

    class Meta:
        model = FriendRequest
        fields = ["id", "from_user", "to_user", "status", "created_at"]


class FollowSerializer(serializers.ModelSerializer):
    """
    Serializer for follow relationships between users and academies.

    This serializer provides details about follow relationships, including
    information about the player and academy being followed.

    Fields:
    - id: The unique identifier for the follow relationship.
    - player: The player being followed.
    - academy: The academy being followed.
    - created_at: The timestamp when the follow relationship was created.
    """
    player = FriendListSerializer(read_only=True)
    academy = FriendListSerializer()

    class Meta:
        model = Follow
        fields = ["id", "player", "academy", "created_at"]
