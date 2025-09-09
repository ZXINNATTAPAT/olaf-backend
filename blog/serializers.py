from rest_framework import serializers
from .models import  Post, Comment, PostLike, CommentLike
from authentication.models import Account

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'username', 'first_name', 'last_name', 'phone', 'email']
        # fields = ['id', 'username','email']

class PostSerializer(serializers.ModelSerializer):
    comment_count = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    image_secure_url = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['post_id', 'post_text', 'post_datetime', 'user', 'image', 'image_url', 'image_secure_url', 'header', 'short', 'like_count', 'comment_count']

    def get_comment_count(self, obj):
        return obj.comments.count()
    
    def get_image_url(self, obj):
        return obj.image_url
    
    def get_image_secure_url(self, obj):
        return obj.image_secure_url
    
class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ['comment_id', 'post', 'user', 'comment_datetime', 'comment_text', 'like_count']

class PostLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostLike
        fields = ['post', 'user']

class CommentLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentLike
        fields = ['comment', 'user', 'id']
