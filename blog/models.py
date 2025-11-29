from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from authentication.models import Account
from cloudinary.models import CloudinaryField

class Post(models.Model):
    post_id = models.AutoField(primary_key=True)
    header = models.CharField(max_length=255, blank=True, null=True)
    short = models.CharField(max_length=255, blank=True, null=True)
    post_text = models.TextField()
    post_datetime = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='posts')
    image = CloudinaryField('image', folder='posts/images/', blank=True, null=True)  # Keep for backward compatibility
    images = GenericRelation('shared_images.SharedImage', related_query_name='post')  # New shared images

    def __str__(self):
        return self.header if self.header else 'Untitled Post'

    @property
    def like_count(self):
        return self.likes.count()
    
    @property
    def image_url(self):
        """Return the URL of the image from Cloudinary"""
        if self.image:
            return self.image.url
        return None
    
    @property
    def image_public_id(self):
        """Return the public ID of the image in Cloudinary"""
        if self.image:
            return self.image.public_id
        return None
    
    @property
    def image_secure_url(self):
        """Return the secure URL of the image from Cloudinary"""
        if self.image:
            return self.image.build_url(secure=True)
        return None
    
    @property
    def primary_image(self):
        """Return the primary shared image"""
        return self.images.filter(is_primary=True).first()
    
    @property
    def primary_image_url(self):
        """Return the URL of the primary shared image"""
        primary = self.primary_image
        if primary:
            return primary.image_url
        # Fallback to old image field
        return self.image_url
    
    @property
    def all_images(self):
        """Return all shared images for this post"""
        return self.images.all().order_by('sort_order', 'uploaded_at')
    
    @property
    def image_count(self):
        """Return the count of shared images"""
        return self.images.count()
    
    class Meta:
        ordering = ['-post_datetime']

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
