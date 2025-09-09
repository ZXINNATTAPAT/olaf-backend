from rest_framework import serializers
from .models import  Post, Comment, PostLike, CommentLike
from authentication.models import Account

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'username', 'first_name', 'last_name', 'phone', 'email', 'created_at']
        read_only_fields = ['id', 'created_at']

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Comment
        fields = ['comment_id', 'post', 'user', 'user_id', 'comment_datetime', 'comment_text', 'like_count']
        read_only_fields = ['comment_id', 'comment_datetime']

class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    comment_count = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    image_secure_url = serializers.SerializerMethodField()
    liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'post_id', 'post_text', 'post_datetime', 'user', 'user_id', 
            'image', 'image_url', 'image_secure_url', 'header', 'short', 
            'like_count', 'comment_count', 'comments', 'liked'
        ]
        read_only_fields = ['post_id', 'post_datetime']

    def get_comment_count(self, obj):
        return obj.comments.count()
    
    def get_image_url(self, obj):
        return obj.image_url
    
    def get_image_secure_url(self, obj):
        return obj.image_secure_url
    
    def get_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

class PostLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostLike
        fields = ['post', 'user']

class CommentLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentLike
        fields = ['comment', 'user', 'id']
