from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from cloudinary.models import CloudinaryField

User = get_user_model()

class CloudDiary(models.Model):
    title = models.CharField(max_length=200, null=False, blank=False)
    content = models.TextField(null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clouddiaries')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Cloud Diary'
        verbose_name_plural = 'Cloud Diaries'
    
    def __str__(self):
        return f"{self.title} by {self.author.username}"

class CloudDiaryImage(models.Model):
    clouddiary = models.ForeignKey(CloudDiary, on_delete=models.CASCADE, related_name='images')
    image = CloudinaryField('image', folder='clouddiary/images/')
    caption = models.CharField(max_length=255, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['uploaded_at']
        verbose_name = 'Cloud Diary Image'
        verbose_name_plural = 'Cloud Diary Images'
    
    def __str__(self):
        return f"Image for {self.clouddiary.title}"
    
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