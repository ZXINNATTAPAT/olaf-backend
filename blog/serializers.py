from rest_framework import serializers
from .models import  Post, Comment, PostLike, CommentLike
from authentication.models import Account

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'username', 'first_name', 'last_name', 'phone', 'email']
        # fields = ['id', 'username','email']

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['post_id', 'post_text', 'post_datetime', 'user', 'image', 'header', 'short', 'like_count']

class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ['comment_id', 'post', 'user', 'comment_datetime', 'comment_text', 'like_count']

class PostLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostLike
        fields = ['post', 'user', 'id']

class CommentLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentLike
        fields = ['comment', 'user', 'id']
