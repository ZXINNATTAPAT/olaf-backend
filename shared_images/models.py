from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from cloudinary.models import CloudinaryField

class SharedImage(models.Model):
    """
    Generic image model that can be used by any model in the system
    """
    image = CloudinaryField('image', folder='shared/images/')
    caption = models.CharField(max_length=255, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    # Generic foreign key to link to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Additional metadata
    is_primary = models.BooleanField(default=False)  # Mark primary image
    sort_order = models.PositiveIntegerField(default=0)  # For ordering images
    
    class Meta:
        ordering = ['sort_order', 'uploaded_at']
        verbose_name = 'Shared Image'
        verbose_name_plural = 'Shared Images'
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['is_primary']),
        ]
    
    def __str__(self):
        return f"Image for {self.content_object} - {self.caption or 'No caption'}"
    
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
    
    @classmethod
    def get_images_for_object(cls, obj):
        """Get all images for a specific object"""
        content_type = ContentType.objects.get_for_model(obj)
        return cls.objects.filter(
            content_type=content_type,
            object_id=obj.pk
        ).order_by('sort_order', 'uploaded_at')
    
    @classmethod
    def get_primary_image_for_object(cls, obj):
        """Get the primary image for a specific object"""
        content_type = ContentType.objects.get_for_model(obj)
        return cls.objects.filter(
            content_type=content_type,
            object_id=obj.pk,
            is_primary=True
        ).first()