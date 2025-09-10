from rest_framework import serializers
from .models import SharedImage

class SharedImageSerializer(serializers.ModelSerializer):
    image_url = serializers.ReadOnlyField()
    image_public_id = serializers.ReadOnlyField()
    image_secure_url = serializers.ReadOnlyField()
    
    class Meta:
        model = SharedImage
        fields = [
            'id', 'image', 'caption', 'image_url', 'image_public_id', 
            'image_secure_url', 'uploaded_at', 'is_primary', 'sort_order'
        ]
        read_only_fields = ['id', 'uploaded_at']

class SharedImageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating images with automatic object linking"""
    
    class Meta:
        model = SharedImage
        fields = ['image', 'caption', 'is_primary', 'sort_order']
    
    def create(self, validated_data):
        # The content_object will be set in the view
        return super().create(validated_data)

class SharedImageUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating image metadata"""
    
    class Meta:
        model = SharedImage
        fields = ['caption', 'is_primary', 'sort_order']
    
    def update(self, instance, validated_data):
        # Only allow updating metadata, not the image itself
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
