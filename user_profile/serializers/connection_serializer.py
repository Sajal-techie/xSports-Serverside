from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import FriendRequest, Follow
from users.serializers.user_serializer import CustomUsersSerializer

User = get_user_model()

class FriendListSerializer(serializers.ModelSerializer):
    profile_photo = serializers.SerializerMethodField('get_profile_photo')
    # sports = serializers.StringRelatedField(many=True, source='sport_set')
    bio = serializers.SerializerMethodField('get_bio')

    class Meta:
        model = User
        fields = ['id', 'username', 'is_academy', 'profile_photo', 'bio', 
                #   'sports'
                  ]

    def get_profile_photo(self, obj):
        print(obj)
        if hasattr(obj, 'userprofile') and obj.userprofile.profile_photo:
            return obj.userprofile.profile_photo.url
        return None

    def get_bio(self, obj):
        if hasattr(obj, 'bio') and obj.userprofile.bio:
            return obj.userprofile.bio


class FriendRequestSerializer(serializers.ModelSerializer):
    from_user = FriendListSerializer(read_only=True)
    to_user = FriendListSerializer(required=False) 
    
    class Meta:
        model = FriendRequest
        fields = ['id', 'from_user', 'to_user', 'status', 'created_at']
    

class FollowSerializer(serializers.ModelSerializer):
    player = FriendListSerializer(read_only=True)
    academy = FriendListSerializer()

    class Meta:
        model = Follow
        fields = ['id', 'player', 'academy', 'created_at']