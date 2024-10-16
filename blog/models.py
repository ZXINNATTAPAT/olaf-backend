from django.db import models
from authentication.models import Account

class Post(models.Model):
    post_id = models.AutoField(primary_key=True)
    header = models.CharField(max_length=255, blank=True, null=True)
    short = models.CharField(max_length=255, blank=True, null=True)
    post_text = models.TextField()
    post_datetime = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='posts')
    image = models.ImageField(upload_to='posts/images/', blank=True, null=True)

    def __str__(self):
        return self.header if self.header else 'Untitled Post'

    @property
    def like_count(self):
        return self.likes.count()

class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='comments')
    comment_datetime = models.DateTimeField(auto_now_add=True)
    comment_text = models.TextField()

    def __str__(self):
        return f'Comment by {self.user.username} on {self.post.header if self.post.header else "Untitled Post"}'

    @property
    def like_count(self):
        return self.likes.count()

class PostLike(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='post_likes')

    class Meta:
        unique_together = ('post', 'user')

    def __str__(self):
        return f'{self.user.username} likes {self.post.header if self.post.header else "an Untitled Post"}'

class CommentLike(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='comment_likes')

    class Meta:
        unique_together = ('comment', 'user')

    def __str__(self):
        return f'{self.user.username} likes a comment on {self.comment.post.header if self.comment.post.header else "Untitled Post"}'
