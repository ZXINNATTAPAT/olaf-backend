from django.db import models
from django.core.validators import FileExtensionValidator
from authentication.models import Account
from utils.helpers import resize_image, generate_unique_filename

class Post(models.Model):
    post_id = models.AutoField(primary_key=True)
    header = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        help_text="Post title"
    )
    short = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        help_text="Short description or summary"
    )
    post_text = models.TextField(
        help_text="Main content of the post"
    )
    post_datetime = models.DateTimeField(
        auto_now_add=True,
        help_text="When the post was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the post was last updated"
    )
    user = models.ForeignKey(
        Account, 
        on_delete=models.CASCADE, 
        related_name='posts',
        help_text="Author of the post"
    )
    image = models.ImageField(
        upload_to='posts/images/', 
        blank=True, 
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif'])],
        help_text="Post image (JPG, PNG, GIF only)"
    )
    is_published = models.BooleanField(
        default=True,
        help_text="Whether the post is published"
    )

    def __str__(self):
        return self.header if self.header else 'Untitled Post'

    @property
    def like_count(self):
        return self.likes.count()

    def save(self, *args, **kwargs):
        # Resize image if it exists
        if self.image:
            self.image = resize_image(self.image)
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'posts'
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'
        ordering = ['-post_datetime']

class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    post = models.ForeignKey(
        Post, 
        on_delete=models.CASCADE, 
        related_name='comments',
        help_text="Post being commented on"
    )
    user = models.ForeignKey(
        Account, 
        on_delete=models.CASCADE, 
        related_name='comments',
        help_text="User who made the comment"
    )
    comment_datetime = models.DateTimeField(
        auto_now_add=True,
        help_text="When the comment was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the comment was last updated"
    )
    comment_text = models.TextField(
        help_text="Content of the comment"
    )
    is_edited = models.BooleanField(
        default=False,
        help_text="Whether the comment has been edited"
    )

    def __str__(self):
        return f'Comment by {self.user.username} on {self.post.header if self.post.header else "Untitled Post"}'

    @property
    def like_count(self):
        return self.likes.count()

    class Meta:
        db_table = 'comments'
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        ordering = ['-comment_datetime']

class PostLike(models.Model):
    post = models.ForeignKey(
        Post, 
        on_delete=models.CASCADE, 
        related_name='likes',
        help_text="Post being liked"
    )
    user = models.ForeignKey(
        Account, 
        on_delete=models.CASCADE, 
        related_name='post_likes',
        help_text="User who liked the post"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the like was created"
    )

    class Meta:
        unique_together = ('post', 'user')
        db_table = 'post_likes'
        verbose_name = 'Post Like'
        verbose_name_plural = 'Post Likes'

    def __str__(self):
        return f'{self.user.username} likes {self.post.header if self.post.header else "an Untitled Post"}'

class CommentLike(models.Model):
    comment = models.ForeignKey(
        Comment, 
        on_delete=models.CASCADE, 
        related_name='likes',
        help_text="Comment being liked"
    )
    user = models.ForeignKey(
        Account, 
        on_delete=models.CASCADE, 
        related_name='comment_likes',
        help_text="User who liked the comment"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the like was created"
    )

    class Meta:
        unique_together = ('comment', 'user')
        db_table = 'comment_likes'
        verbose_name = 'Comment Like'
        verbose_name_plural = 'Comment Likes'

    def __str__(self):
        return f'{self.user.username} likes a comment on {self.comment.post.header if self.comment.post.header else "Untitled Post"}'
