from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from .models import SharedImage
from .serializers import (
    SharedImageSerializer, 
    SharedImageCreateSerializer, 
    SharedImageUpdateSerializer,
    SharedImagePathSerializer
)
from authentication.authenticate import CustomAuthentication

class SharedImageListCreateView(generics.ListCreateAPIView):
    """List and create images for a specific object"""
    serializer_class = SharedImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [CustomAuthentication]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        # Get the object type and ID from URL parameters
        content_type_id = self.kwargs.get('content_type_id')
        object_id = self.kwargs.get('object_id')
        
        if content_type_id and object_id:
            content_type = ContentType.objects.get_for_id(content_type_id)
            return SharedImage.objects.filter(
                content_type=content_type,
                object_id=object_id
            ).order_by('sort_order', 'uploaded_at')
        
        return SharedImage.objects.none()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SharedImageCreateSerializer
        return SharedImageSerializer
    
    def perform_create(self, serializer):
        # Set the content object from URL parameters
        content_type_id = self.kwargs.get('content_type_id')
        object_id = self.kwargs.get('object_id')
        
        content_type = ContentType.objects.get_for_id(content_type_id)
        obj = content_type.get_object_for_this_type(pk=object_id)
        
        serializer.save(content_object=obj)

class SharedImageDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a specific image"""
    serializer_class = SharedImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [CustomAuthentication]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        return SharedImage.objects.all()
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return SharedImageUpdateSerializer
        return SharedImageSerializer

@api_view(['POST'])
@authentication_classes([CustomAuthentication])
@permission_classes([permissions.IsAuthenticated])
def upload_image_to_object(request, content_type_id, object_id):
    """Upload an image to a specific object"""
    try:
        content_type = ContentType.objects.get_for_id(content_type_id)
        obj = content_type.get_object_for_this_type(pk=object_id)
    except (ContentType.DoesNotExist, Exception):
        return Response(
            {"error": "Object not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = SharedImageCreateSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(content_object=obj)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@authentication_classes([CustomAuthentication])
@permission_classes([permissions.IsAuthenticated])
def add_image_path_to_object(request, content_type_id, object_id):
    """Add an image path to a specific object (for frontend-uploaded images)"""
    try:
        content_type = ContentType.objects.get_for_id(content_type_id)
        obj = content_type.get_object_for_this_type(pk=object_id)
    except (ContentType.DoesNotExist, Exception):
        return Response(
            {"error": "Object not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = SharedImagePathSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(content_object=obj)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@authentication_classes([CustomAuthentication])
@permission_classes([permissions.IsAuthenticated])
def get_object_images(request, content_type_id, object_id):
    """Get all images for a specific object"""
    try:
        content_type = ContentType.objects.get_for_id(content_type_id)
        obj = content_type.get_object_for_this_type(pk=object_id)
    except (ContentType.DoesNotExist, Exception):
        return Response(
            {"error": "Object not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    images = SharedImage.get_images_for_object(obj)
    serializer = SharedImageSerializer(images, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@authentication_classes([CustomAuthentication])
@permission_classes([permissions.IsAuthenticated])
def get_primary_image(request, content_type_id, object_id):
    """Get the primary image for a specific object"""
    try:
        content_type = ContentType.objects.get_for_id(content_type_id)
        obj = content_type.get_object_for_this_type(pk=object_id)
    except (ContentType.DoesNotExist, Exception):
        return Response(
            {"error": "Object not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    primary_image = SharedImage.get_primary_image_for_object(obj)
    if primary_image:
        serializer = SharedImageSerializer(primary_image)
        return Response(serializer.data)
    return Response({"message": "No primary image found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PATCH'])
@authentication_classes([CustomAuthentication])
@permission_classes([permissions.IsAuthenticated])
def set_primary_image(request, image_id):
    """Set an image as primary for its object"""
    image = get_object_or_404(SharedImage, id=image_id)
    
    # Remove primary status from other images of the same object
    SharedImage.objects.filter(
        content_type=image.content_type,
        object_id=image.object_id
    ).update(is_primary=False)
    
    # Set this image as primary
    image.is_primary = True
    image.save()
    
    serializer = SharedImageSerializer(image)
    return Response(serializer.data)

@api_view(['DELETE'])
@authentication_classes([CustomAuthentication])
@permission_classes([permissions.IsAuthenticated])
def delete_image(request, image_id):
    """Delete an image"""
    image = get_object_or_404(SharedImage, id=image_id)
    image.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)