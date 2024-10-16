from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import  Post, Comment, PostLike, CommentLike
from authentication.models import Account
from .serializers import UserSerializer, PostSerializer, CommentSerializer, PostLikeSerializer, CommentLikeSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = UserSerializer

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        # รวมข้อมูลยอดไลค์ใน response
        response_data = serializer.data
        response_data['like_count'] = instance.like_count  # เพิ่มจำนวนไลค์
        response_data['liked'] = self.get_like_status(instance, request.user)  # ตรวจสอบสถานะไลค์ของผู้ใช้
        response_data['comment_count'] = instance.comments.count()

        return Response(response_data)

    def get_like_status(self, post, user):
        if user.is_authenticated:
            return post.likes.filter(user=user).exists()
        return False

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        # รวมข้อมูลยอดไลค์ใน response
        response_data = serializer.data
        response_data['like_count'] = instance.like_count  # เพิ่มจำนวนไลค์
        response_data['liked'] = self.get_like_status(instance, request.user)  # ตรวจสอบสถานะไลค์ของผู้ใช้

        return Response(response_data)

    def get_like_status(self, post, user):
        if user.is_authenticated:
            return post.likes.filter(user=user).exists()
        return False

class PostLikeViewSet(viewsets.ModelViewSet):
    queryset = PostLike.objects.all()
    serializer_class = PostLikeSerializer
    lookup_field = 'post_id'  # ใช้ 'post_id' ในการค้นหาไลค์

    def create(self, request):
        post_id = request.data.get('post')
        user_id = request.data.get('user', None)  # Allow anonymous likes

        post = Post.objects.get(pk=post_id)

        if user_id:
            user = Account.objects.get(pk=user_id)
            post_like, created = PostLike.objects.get_or_create(post=post, user=user)
            like_status = created
        else:
            # Handle anonymous like (e.g., increment a counter or track IPs)
            like_status = True  # Assume the like goes through

# Ensure like_count is updated correctly here
        like_count = post.like_count  # Call the like_count property
        return Response({
            'liked': like_status,
            'like_count': like_count  # Ensure like_count is included in response
        }, status=status.HTTP_201_CREATED if like_status else status.HTTP_200_OK)
    
    def destroy(self, request, post_id=None, user_id=None):
        try:
            # ค้นหาไลค์ที่ตรงกับ post_id และ user_id
            post_like = PostLike.objects.get(post_id=post_id, user_id=user_id)
            post_like.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)
        except PostLike.DoesNotExist:
            return Response({'detail': 'Like not found'}, status=status.HTTP_404_NOT_FOUND)
    
class CommentLikeViewSet(viewsets.ModelViewSet):
    queryset = CommentLike.objects.all()
    serializer_class = CommentLikeSerializer
    lookup_field = 'comment_id'  # ใช้ 'comment_id' ในการค้นหาไลค์

    def create(self, request):
        comment_id = request.data.get('comment')
        user_id = request.data.get('user', None)  # Allow anonymous likes

        comment = Comment.objects.get(pk=comment_id)

        if user_id:
            user = Account.objects.get(pk=user_id)
            comment_like, created = CommentLike.objects.get_or_create(comment=comment, user=user)
            like_status = created
        else:
            # Handle anonymous like (e.g., increment a counter or track IPs)
            like_status = True  # Assume the like goes through
            # คุณอาจต้องการเพิ่มการจัดการสำหรับการไลค์แบบไม่ระบุชื่อ

        # อัปเดตจำนวนไลค์ในความคิดเห็น
        # comment.like_count = CommentLike.objects.filter(comment=comment).count()
        # comment.save()

        # Ensure like_count is updated correctly here
        like_count = comment.like_count  # Call the like_count property
        return Response({
            'liked': like_status,
            'like_count': like_count  # Ensure like_count is included in response
        }, status=status.HTTP_201_CREATED if like_status else status.HTTP_200_OK)

    def destroy(self, request, comment_id=None, user_id=None):
        try:
            # ค้นหาไลค์ที่ตรงกับ comment_id และ user_id
            comment_like = CommentLike.objects.get(comment_id=comment_id, user_id=user_id)
            comment_like.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)
        except CommentLike.DoesNotExist:
            return Response({'detail': 'Like not found'}, status=status.HTTP_404_NOT_FOUND)
