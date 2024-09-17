from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class User(AbstractUser):
    phone = models.CharField(max_length=15, blank=True, null=True)
    social_acc = models.CharField(max_length=255, blank=True, null=True)

class Post(models.Model):
    post_id = models.AutoField(primary_key=True)
    post_text = models.TextField()
    post_datetime = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')

class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    comment_datetime = models.DateTimeField(auto_now_add=True)
    comment_text = models.TextField()

class PostLike(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_likes')

    class Meta:
        unique_together = ('post', 'user')

class CommentLike(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_likes')

    class Meta:
        unique_together = ('comment', 'user')
