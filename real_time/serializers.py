from django.db.models import Q
from rest_framework import serializers
from user_profile.serializers.connection_serializer import FriendListSerializer

from .models import Chat, Notification, Users


class ChatSerializer(serializers.ModelSerializer):
    sender = FriendListSerializer(read_only=True)
    receiver = FriendListSerializer(read_only=True)

    class Meta:
        model = Chat
        fields = ["id", "sender", "receiver", "message", "thread_name", "date"]


class ChatListUserSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    profile_photo = serializers.SerializerMethodField()

    class Meta:
        model = Users
        fields = ["id", "username", "last_message", "profile_photo"]

    def get_last_message(self, obj):
        current_user = self.context["request"].user
        last_chat = (
            Chat.objects.filter(
                (Q(sender=current_user) & Q(receiver=obj))
                | (Q(sender=obj) & Q(receiver=current_user))
            )
            .order_by("-date")
            .first()
        )

        if last_chat:
            return {
                "message": last_chat.message,
                "date": last_chat.date,
                "is_sender": last_chat.sender == current_user,
                "read": last_chat.read if last_chat.sender == current_user else True,
            }
        return None

    def get_profile_photo(self, obj):
        print(obj)
        if hasattr(obj, "userprofile") and obj.userprofile.profile_photo:
            return obj.userprofile.profile_photo.url
        return None


class NotificationSerializer(serializers.ModelSerializer):
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
