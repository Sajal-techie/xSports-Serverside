from rest_framework import serializers
from .models import Post, Comment, Like
from user_profile.models import Follow, FriendRequest
from real_time.models import Notification
from real_time.task import send_notification

class CommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()
    user = serializers.ReadOnlyField(source='user.username')
    profile_photo = serializers.ImageField(source='user.userprofile.profile_photo',read_only=True)
    user_id = serializers.ReadOnlyField(source='user.id')
    is_academy = serializers.ReadOnlyField(source='user.is_academy')

    class Meta:
        model = Comment
        fields = ['id', 'user', 'created_at', 'replies', 'content', 'parent', 
                  'profile_photo', 'user_id', 'is_academy' ] 

    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return []


class PostSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    bio = serializers.ReadOnlyField(source='user.userprofile.bio',read_only=True)
    profile_photo = serializers.ImageField(source='user.userprofile.profile_photo',read_only=True)
    comments = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    is_liked_by_current_user = serializers.SerializerMethodField()
    is_own_post = serializers.SerializerMethodField()
    is_academy = serializers.ReadOnlyField(source='user.is_academy')
    user_id = serializers.ReadOnlyField(source='user.id')
    relationship_status = serializers.SerializerMethodField() 

    class Meta:
        model = Post
        fields = ['id','user','image','video', 'content','created_at', 'bio', 'is_own_post', 'is_academy', 'relationship_status',
                  'updated_at','comments', 'likes_count','profile_photo', 'is_liked_by_current_user', 'user_id']
    
    def create(self, validated_data):
        user = self.context['request'].user
        print(user,validated_data)
        post = Post.objects.create(user=user, **validated_data) 
       
        notification_type = 'new_post'
        text = f"{user.username} added a new post"
        link = f"/view_post_details/{post.id}"

        if user.is_academy:
            receivers_list = list(Follow.objects.filter(
                                academy=user,
                            ).values_list('player__id',flat=True))
        else:
            receivers_list = list(user.friends.all().values_list('id',flat=True))
        
        print(receivers_list,'recivers list',user.is_academy)
        send_notification.delay(notification_type, text, link,user.id, receivers_list)


        return post

    def get_likes_count(self, obj):
        return obj.likes.count()
    
    def get_is_liked_by_current_user(self, obj):
        user = self.context['request'].user
        return obj.likes.filter(user=user).exists()
    
    def get_comments(self, obj):
        return CommentSerializer(obj.comments.filter(parent=None), many=True).data #filtering comments using post(reverse relation)
    
    def get_is_own_post(self,obj):
        user = self.context['request'].user
        return obj.user == user
    
    def get_relationship_status(self, obj):
        current_user = self.context['request'].user
        post_author = obj.user

        if current_user == post_author:
            return 'self'

        if post_author.is_academy:
            following = Follow.objects.filter(player=current_user, academy=post_author).exists()
            return 'following' if following else 'follow'

        if current_user.is_academy:
            following = Follow.objects.filter(player=post_author, academy=current_user).exists()
            return 'follower' if following else 'notfollower'

        friend_request = FriendRequest.objects.filter(from_user=post_author, to_user=current_user).first()
        if friend_request:
            return 'received'

        friend_request = FriendRequest.objects.filter(from_user=current_user, to_user=post_author).first()
        if friend_request:
            return 'sent'

        if current_user.friends.filter(id=post_author.id).exists():
            return 'friends'

        return 'none'

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'post', 'user', 'created_at', 'updated_at']