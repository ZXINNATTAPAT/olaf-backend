from rest_framework import serializers
from .models import User, Post, Comment, PostLike, CommentLike

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'phone', 'social_acc', 'email']

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['post_id', 'post_text', 'post_datetime', 'user']

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['comment_id', 'post', 'user', 'comment_datetime', 'comment_text']

class PostLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostLike
        fields = ['post', 'user']

class CommentLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentLike
        fields = ['comment', 'user']

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'phone', 'social_acc', 'email')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            phone=validated_data.get('phone'),
            social_acc=validated_data.get('social_acc'),
            email=validated_data.get('email')
        )
        return user
