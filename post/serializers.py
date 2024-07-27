from rest_framework import serializers
from .models import Post, Comment, Like


class CommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()
    user = serializers.ReadOnlyField(source='user.username')
    profile_photo = serializers.ImageField(source='user.userprofile.profile_photo',read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'created_at', 'replies', 'content', 'parent','profile_photo'] 

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

    class Meta:
        model = Post
        fields = ['id','user','image','video', 'content','created_at', 'bio',
                  'updated_at','comments', 'likes_count','profile_photo', 'is_liked_by_current_user']
     
    def create(self, validated_data):
        print(self.context['request'].user,validated_data)
        return Post.objects.create(user=self.context['request'].user, **validated_data) 

    def get_likes_count(self, obj):
        return obj.likes.count()
    
    def get_is_liked_by_current_user(self, obj):
        user = self.context['request'].user
        print(obj, 'obj in get is liked',user)
        return obj.likes.filter(user=user).exists()
    
    def get_comments(self, obj):
        print(obj,'in comentmehtod field')
        return CommentSerializer(obj.comments.filter(parent=None), many=True).data #filtering comments using post(reverse relation)


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'post', 'user', 'created_at', 'updated_at']