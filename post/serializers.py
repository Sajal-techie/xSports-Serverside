from real_time.task import send_notification
from rest_framework import serializers
from user_profile.models import Follow, FriendRequest

from .models import Comment, Like, Post


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for Comment model.

    Includes fields for user details, replies, and other comment-specific attributes.
    """
    replies = serializers.SerializerMethodField()
    user = serializers.ReadOnlyField(source="user.username")
    profile_photo = serializers.ImageField(
        source="user.userprofile.profile_photo", read_only=True
    )
    user_id = serializers.ReadOnlyField(source="user.id")
    is_academy = serializers.ReadOnlyField(source="user.is_academy")

    class Meta:
        model = Comment
        fields = [
            "id",
            "user",
            "created_at",
            "replies",
            "content",
            "parent",
            "profile_photo",
            "user_id",
            "is_academy",
        ]

    def get_replies(self, obj):
        """
        Return a list of replies for the comment.

        If there are no replies, return an empty list.
        """
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return []


class PostSerializer(serializers.ModelSerializer):
    """
    Serializer for Post model.

    Includes fields for user details, post content, and additional computed fields like likes count,
    comments, and relationship status.
    """
    user = serializers.ReadOnlyField(source="user.username")
    bio = serializers.ReadOnlyField(source="user.userprofile.bio", read_only=True)
    profile_photo = serializers.ImageField(
        source="user.userprofile.profile_photo", read_only=True
    )
    comments = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    is_liked_by_current_user = serializers.SerializerMethodField()
    is_own_post = serializers.SerializerMethodField()
    is_academy = serializers.ReadOnlyField(source="user.is_academy")
    user_id = serializers.ReadOnlyField(source="user.id")
    relationship_status = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "user",
            "image",
            "video",
            "content",
            "created_at",
            "bio",
            "is_own_post",
            "is_academy",
            "relationship_status",
            "updated_at",
            "comments",
            "likes_count",
            "profile_photo",
            "is_liked_by_current_user",
            "user_id",
        ]

    def create(self, validated_data):
        """
        Create a new Post and send a notification to relevant users.

        Determines the recipients based on whether the user is an academy or player and sends a notification
        about the new post.
        """
        user = self.context["request"].user
        post = Post.objects.create(user=user, **validated_data)

        notification_type = "new_post"
        text = f"{user.username} added a new post"
        link = f"/view_post_details/{post.id}"

        if user.is_academy:
            receivers_list = list(
                Follow.objects.filter(
                    academy=user,
                ).values_list("player__id", flat=True)
            )
        else:
            receivers_list = list(user.friends.all().values_list("id", flat=True))

        send_notification.delay(notification_type, text, link, user.id, receivers_list)

        return post

    def get_likes_count(self, obj):
        """
        Return the count of likes for the post.
        """
        return obj.likes.count()

    def get_is_liked_by_current_user(self, obj):
        """
        Check if the current user has liked the post.
        """
        user = self.context["request"].user
        return obj.likes.filter(user=user).exists()

    def get_comments(self, obj):
        """
        Return a list of comments for the post, excluding replies to other comments.
        """
        return CommentSerializer(
            obj.comments.filter(parent=None), many=True
        ).data  

    def get_is_own_post(self, obj):
        """
        Check if the post was created by the current user.
        """
        user = self.context["request"].user
        return obj.user == user

    def get_relationship_status(self, obj):
        """
        Determine the relationship status between the current user and the post author.
        
        Possible statuses:
        - "self" if the current user is the author
        - "following" if the current user follows the academy
        - "follow" if the current user should follow the academy
        - "follower" if the post author follows the current user
        - "notfollower" if the post author does not follow the current user
        - "received" if there's a received friend request
        - "sent" if there's a sent friend request
        - "friends" if the users are friends
        - "none" if none of the above
        """
        current_user = self.context["request"].user
        post_author = obj.user

        if current_user == post_author:
            return "self"

        if post_author.is_academy:
            following = Follow.objects.filter(
                player=current_user, academy=post_author
            ).exists()
            return "following" if following else "follow"

        if current_user.is_academy:
            following = Follow.objects.filter(
                player=post_author, academy=current_user
            ).exists()
            return "follower" if following else "notfollower"

        friend_request = FriendRequest.objects.filter(
            from_user=post_author, to_user=current_user
        ).first()
        if friend_request:
            return "received"

        friend_request = FriendRequest.objects.filter(
            from_user=current_user, to_user=post_author
        ).first()
        if friend_request:
            return "sent"

        if current_user.friends.filter(id=post_author.id).exists():
            return "friends"

        return "none"


class LikeSerializer(serializers.ModelSerializer):
    """
    Serializer for Like model.

    Includes fields for Like attributes related to a Post.
    """
    class Meta:
        model = Like
        fields = ["id", "post", "user", "created_at", "updated_at"]
