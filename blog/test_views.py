from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from blog.models import Post, Comment, PostLike, CommentLike
from blog.serializers import PostSerializer, CommentSerializer, PostLikeSerializer, CommentLikeSerializer

Account = get_user_model()

class BlogViewsTest(TestCase):
    """Test cases for blog views"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.user = Account.objects.create_user(
            email='test@example.com',
            username='testuser',
            first_name='Test',
            last_name='User',
            phone='1234567890',
            password='testpass123'
        )
        
        self.another_user = Account.objects.create_user(
            email='another@example.com',
            username='anotheruser',
            first_name='Another',
            last_name='User',
            phone='0987654321',
            password='anotherpass123'
        )
        
        self.post = Post.objects.create(
            header='Test Post',
            short='Test short description',
            post_text='This is a test post content',
            user=self.user
        )
        
        self.comment = Comment.objects.create(
            post=self.post,
            user=self.user,
            comment_text='This is a test comment'
        )
        
        # Create access token for authenticated requests
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
    
    def test_post_list_view(self):
        """Test post list endpoint"""
        response = self.client.get('/api/posts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['header'], 'Test Post')
    
    def test_post_detail_view(self):
        """Test post detail endpoint"""
        response = self.client.get(f'/api/posts/{self.post.post_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['header'], 'Test Post')
        self.assertEqual(response.data['like_count'], 0)
        self.assertFalse(response.data['liked'])
        self.assertEqual(response.data['comment_count'], 1)
    
    def test_post_create_view(self):
        """Test post creation endpoint"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        post_data = {
            'header': 'New Post',
            'short': 'New description',
            'post_text': 'New post content',
            'user': self.user.id
        }
        
        response = self.client.post('/api/posts/', post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['header'], 'New Post')
        self.assertEqual(response.data['post_text'], 'New post content')
    
    def test_post_update_view(self):
        """Test post update endpoint"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        update_data = {
            'header': 'Updated Post',
            'post_text': 'Updated content'
        }
        
        response = self.client.patch(f'/api/posts/{self.post.post_id}/', update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['header'], 'Updated Post')
        self.assertEqual(response.data['post_text'], 'Updated content')
    
    def test_post_delete_view(self):
        """Test post deletion endpoint"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        response = self.client.delete(f'/api/posts/{self.post.post_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify post is deleted
        self.assertEqual(Post.objects.count(), 0)
    
    def test_comment_list_view(self):
        """Test comment list endpoint"""
        response = self.client.get('/api/comments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['comment_text'], 'This is a test comment')
    
    def test_comment_detail_view(self):
        """Test comment detail endpoint"""
        response = self.client.get(f'/api/comments/{self.comment.comment_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['comment_text'], 'This is a test comment')
        self.assertEqual(response.data['like_count'], 0)
        self.assertFalse(response.data['liked'])
    
    def test_comment_create_view(self):
        """Test comment creation endpoint"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        comment_data = {
            'post': self.post.post_id,
            'user': self.user.id,
            'comment_text': 'New comment'
        }
        
        response = self.client.post('/api/comments/', comment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['comment_text'], 'New comment')
    
    def test_comment_update_view(self):
        """Test comment update endpoint"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        update_data = {
            'comment_text': 'Updated comment'
        }
        
        response = self.client.patch(f'/api/comments/{self.comment.comment_id}/', update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['comment_text'], 'Updated comment')
    
    def test_comment_delete_view(self):
        """Test comment deletion endpoint"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        response = self.client.delete(f'/api/comments/{self.comment.comment_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify comment is deleted
        self.assertEqual(Comment.objects.count(), 0)
    
    def test_post_like_create_view(self):
        """Test post like creation endpoint"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        like_data = {
            'post': self.post.post_id,
            'user': self.user.id
        }
        
        response = self.client.post('/api/post-likes/', like_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['liked'])
        self.assertEqual(response.data['like_count'], 1)
        
        # Verify like was created
        self.assertTrue(PostLike.objects.filter(post=self.post, user=self.user).exists())
    
    def test_post_like_create_duplicate(self):
        """Test post like creation with duplicate like"""
        # Create first like
        PostLike.objects.create(post=self.post, user=self.user)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        like_data = {
            'post': self.post.post_id,
            'user': self.user.id
        }
        
        response = self.client.post('/api/post-likes/', like_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['liked'])
        self.assertEqual(response.data['like_count'], 1)
    
    def test_post_like_delete_view(self):
        """Test post like deletion endpoint"""
        # Create a like first
        post_like = PostLike.objects.create(post=self.post, user=self.user)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        response = self.client.delete(f'/api/post-likes/{self.post.post_id}/?user_id={self.user.id}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify like is deleted
        self.assertFalse(PostLike.objects.filter(post=self.post, user=self.user).exists())
    
    def test_post_like_delete_not_found(self):
        """Test post like deletion when like doesn't exist"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        response = self.client.delete(f'/api/post-likes/{self.post.post_id}/?user_id={self.user.id}')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], 'Like not found')
    
    def test_comment_like_create_view(self):
        """Test comment like creation endpoint"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        like_data = {
            'comment': self.comment.comment_id,
            'user': self.user.id
        }
        
        response = self.client.post('/api/comment-likes/', like_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['liked'])
        self.assertEqual(response.data['like_count'], 1)
        
        # Verify like was created
        self.assertTrue(CommentLike.objects.filter(comment=self.comment, user=self.user).exists())
    
    def test_comment_like_create_duplicate(self):
        """Test comment like creation with duplicate like"""
        # Create first like
        CommentLike.objects.create(comment=self.comment, user=self.user)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        like_data = {
            'comment': self.comment.comment_id,
            'user': self.user.id
        }
        
        response = self.client.post('/api/comment-likes/', like_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['liked'])
        self.assertEqual(response.data['like_count'], 1)
    
    def test_comment_like_delete_view(self):
        """Test comment like deletion endpoint"""
        # Create a like first
        comment_like = CommentLike.objects.create(comment=self.comment, user=self.user)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        response = self.client.delete(f'/api/comment-likes/{self.comment.comment_id}/?user_id={self.user.id}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify like is deleted
        self.assertFalse(CommentLike.objects.filter(comment=self.comment, user=self.user).exists())
    
    def test_comment_like_delete_not_found(self):
        """Test comment like deletion when like doesn't exist"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        response = self.client.delete(f'/api/comment-likes/{self.comment.comment_id}/?user_id={self.user.id}')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], 'Like not found')
    
    def test_post_like_anonymous_user(self):
        """Test post like creation with anonymous user"""
        like_data = {
            'post': self.post.post_id
            # No user_id provided
        }
        
        response = self.client.post('/api/post-likes/', like_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['liked'])
    
    def test_comment_like_anonymous_user(self):
        """Test comment like creation with anonymous user"""
        like_data = {
            'comment': self.comment.comment_id
            # No user_id provided
        }
        
        response = self.client.post('/api/comment-likes/', like_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['liked'])
    
    def test_post_like_count_increment(self):
        """Test that post like count increments correctly"""
        # Initial like count should be 0
        response = self.client.get(f'/api/posts/{self.post.post_id}/')
        self.assertEqual(response.data['like_count'], 0)
        
        # Create a like
        PostLike.objects.create(post=self.post, user=self.user)
        
        # Like count should now be 1
        response = self.client.get(f'/api/posts/{self.post.post_id}/')
        self.assertEqual(response.data['like_count'], 1)
        
        # Create another like from different user
        PostLike.objects.create(post=self.post, user=self.another_user)
        
        # Like count should now be 2
        response = self.client.get(f'/api/posts/{self.post.post_id}/')
        self.assertEqual(response.data['like_count'], 2)
    
    def test_comment_like_count_increment(self):
        """Test that comment like count increments correctly"""
        # Initial like count should be 0
        response = self.client.get(f'/api/comments/{self.comment.comment_id}/')
        self.assertEqual(response.data['like_count'], 0)
        
        # Create a like
        CommentLike.objects.create(comment=self.comment, user=self.user)
        
        # Like count should now be 1
        response = self.client.get(f'/api/comments/{self.comment.comment_id}/')
        self.assertEqual(response.data['like_count'], 1)
    
    def test_post_like_status_authenticated_user(self):
        """Test post like status for authenticated user"""
        # User hasn't liked the post yet
        response = self.client.get(f'/api/posts/{self.post.post_id}/')
        self.assertFalse(response.data['liked'])
        
        # Create a like
        PostLike.objects.create(post=self.post, user=self.user)
        
        # Now user has liked the post
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.get(f'/api/posts/{self.post.post_id}/')
        self.assertTrue(response.data['liked'])
    
    def test_comment_like_status_authenticated_user(self):
        """Test comment like status for authenticated user"""
        # User hasn't liked the comment yet
        response = self.client.get(f'/api/comments/{self.comment.comment_id}/')
        self.assertFalse(response.data['liked'])
        
        # Create a like
        CommentLike.objects.create(comment=self.comment, user=self.user)
        
        # Now user has liked the comment
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.get(f'/api/comments/{self.comment.comment_id}/')
        self.assertTrue(response.data['liked'])
    
    def test_post_comment_count(self):
        """Test that post comment count is correct"""
        # Initial comment count should be 1
        response = self.client.get(f'/api/posts/{self.post.post_id}/')
        self.assertEqual(response.data['comment_count'], 1)
        
        # Create another comment
        Comment.objects.create(
            post=self.post,
            user=self.another_user,
            comment_text='Another comment'
        )
        
        # Comment count should now be 2
        response = self.client.get(f'/api/posts/{self.post.post_id}/')
        self.assertEqual(response.data['comment_count'], 2)
    
    def test_post_like_with_invalid_post_id(self):
        """Test post like creation with invalid post ID"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        like_data = {
            'post': 99999,  # Non-existent post ID
            'user': self.user.id
        }
        
        response = self.client.post('/api/post-likes/', like_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_comment_like_with_invalid_comment_id(self):
        """Test comment like creation with invalid comment ID"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        like_data = {
            'comment': 99999,  # Non-existent comment ID
            'user': self.user.id
        }
        
        response = self.client.post('/api/comment-likes/', like_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
