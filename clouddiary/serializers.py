from rest_framework import serializers
from .models import CloudDiary, CloudDiaryImage
from authentication.serializers import AccountSerializer

class CloudDiaryImageSerializer(serializers.ModelSerializer):
    image_url = serializers.ReadOnlyField()
    image_public_id = serializers.ReadOnlyField()
    image_secure_url = serializers.ReadOnlyField()
    
    class Meta:
        model = CloudDiaryImage
        fields = ['id', 'image', 'caption', 'image_url', 'image_public_id', 'image_secure_url', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']

class CloudDiarySerializer(serializers.ModelSerializer):
    author = AccountSerializer(read_only=True)
    images = CloudDiaryImageSerializer(many=True, read_only=True)
    author_id = serializers.IntegerField(write_only=True)
    image_count = serializers.SerializerMethodField()
    
    class Meta:
        model = CloudDiary
        fields = [
            'id', 'title', 'content', 'author', 'author_id', 
            'created_at', 'updated_at', 'is_public', 'images', 'image_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_image_count(self, obj):
        return obj.images.count()
    
    def create(self, validated_data):
        # Remove author_id from validated_data as it's handled by the view
        validated_data.pop('author_id', None)
        return super().create(validated_data)

class CloudDiaryCreateSerializer(serializers.ModelSerializer):
    images = CloudDiaryImageSerializer(many=True, required=False)
    
    class Meta:
        model = CloudDiary
        fields = ['title', 'content', 'is_public', 'images']
    
    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        clouddiary = CloudDiary.objects.create(**validated_data)
        
        for image_data in images_data:
            CloudDiaryImage.objects.create(clouddiary=clouddiary, **image_data)
        
        return clouddiary

class CloudDiaryUpdateSerializer(serializers.ModelSerializer):
    images = CloudDiaryImageSerializer(many=True, required=False)
    
    class Meta:
        model = CloudDiary
        fields = ['title', 'content', 'is_public', 'images']
    
    def update(self, instance, validated_data):
        images_data = validated_data.pop('images', None)
        
        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Handle images if provided
        if images_data is not None:
            # Clear existing images
            instance.images.all().delete()
            # Add new images
            for image_data in images_data:
                CloudDiaryImage.objects.create(clouddiary=instance, **image_data)
        
        return instance
