from django.db.models import Q
from rest_framework import serializers
from user_profile.serializers.connection_serializer import FriendListSerializer

from .models import Chat, Notification, Users


class ChatSerializer(serializers.ModelSerializer):
    """
    Serializer for the Chat model.
    
    This serializer handles the representation of Chat instances, 
    including the sender and receiver details using the FriendListSerializer.
    """
    sender = FriendListSerializer(read_only=True)
    receiver = FriendListSerializer(read_only=True)

    class Meta:
        model = Chat
        fields = ["id", "sender", "receiver", "message", "thread_name", "date"]


class ChatListUserSerializer(serializers.ModelSerializer):
    """
    Serializer for listing users involved in a chat.
    
    This serializer includes methods to fetch  the profile photo 
    of the user involved in the chat.
    """
    profile_photo = serializers.SerializerMethodField()

    class Meta:
        model = Users
        fields = ["id", "username", "profile_photo"]

    def get_profile_photo(self, obj):
        print(obj)
        if hasattr(obj, "userprofile") and obj.userprofile.profile_photo:
            return obj.userprofile.profile_photo.url
        return None


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Notification model.
    
    This serializer handles the representation of Notification instances,
    including fields such as the sender, text, link, and whether the notification has been seen.
    """
    class Meta:
        model = Notification
        fields = [
            "id",
            "sender",
            "text",
            "link",
            "seen",
            "created_at",
            "notification_type",
        ]
