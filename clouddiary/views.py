from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.db import models
from .models import CloudDiary, CloudDiaryImage
from .serializers import (
    CloudDiarySerializer, 
    CloudDiaryCreateSerializer, 
    CloudDiaryUpdateSerializer,
    CloudDiaryImageSerializer
)
from authentication.authenticate import CustomAuthentication

class CloudDiaryListCreateView(generics.ListCreateAPIView):
    serializer_class = CloudDiarySerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [CustomAuthentication]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        # Return public diaries or user's own diaries
        return CloudDiary.objects.filter(
            models.Q(is_public=True) | models.Q(author=self.request.user)
        ).select_related('author').prefetch_related('images')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CloudDiaryCreateSerializer
        return CloudDiarySerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class CloudDiaryDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CloudDiarySerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [CustomAuthentication]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        # Return public diaries or user's own diaries
        return CloudDiary.objects.filter(
            models.Q(is_public=True) | models.Q(author=self.request.user)
        ).select_related('author').prefetch_related('images')
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return CloudDiaryUpdateSerializer
        return CloudDiarySerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class UserCloudDiaryListView(generics.ListAPIView):
    serializer_class = CloudDiarySerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [CustomAuthentication]
    
    def get_queryset(self):
        # Return only user's own diaries
        return CloudDiary.objects.filter(
            author=self.request.user
        ).select_related('author').prefetch_related('images')
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

@api_view(['POST'])
@authentication_classes([CustomAuthentication])
@permission_classes([permissions.IsAuthenticated])
def add_image_to_clouddiary(request, clouddiary_id):
    """Add an image to an existing clouddiary"""
    clouddiary = get_object_or_404(CloudDiary, id=clouddiary_id, author=request.user)
    
    serializer = CloudDiaryImageSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(clouddiary=clouddiary)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@authentication_classes([CustomAuthentication])
@permission_classes([permissions.IsAuthenticated])
def delete_clouddiary_image(request, image_id):
    """Delete an image from clouddiary"""
    image = get_object_or_404(CloudDiaryImage, id=image_id, clouddiary__author=request.user)
    image.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@authentication_classes([CustomAuthentication])
@permission_classes([permissions.IsAuthenticated])
def get_clouddiary_images(request, clouddiary_id):
    """Get all images for a specific clouddiary"""
    clouddiary = get_object_or_404(CloudDiary, id=clouddiary_id)
    
    # Check if user can access this clouddiary
    if not clouddiary.is_public and clouddiary.author != request.user:
        return Response(
            {"error": "You don't have permission to view this clouddiary"}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    images = clouddiary.images.all()
    serializer = CloudDiaryImageSerializer(images, many=True)
    return Response(serializer.data)