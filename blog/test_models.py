from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from authentication.models import Account
from blog.models import Post, Comment, PostLike, CommentLike
from django.utils import timezone

class BlogModelsTest(TestCase):
    """Test cases for blog models"""
    
    def setUp(self):
        """Set up test data"""
        self.user = Account.objects.create_user(
            email='test@example.com',
            username='testuser',
            first_name='Test',
            last_name='User',
            phone='1234567890',
            password='testpass123'
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
    
    def test_post_creation(self):
        """Test post creation with all fields"""
        post = Post.objects.create(
            header='Another Post',
            short='Another description',
            post_text='Another post content',
            user=self.user
        )
        
        self.assertEqual(post.header, 'Another Post')
        self.assertEqual(post.short, 'Another description')
        self.assertEqual(post.post_text, 'Another post content')
        self.assertEqual(post.user, self.user)
        self.assertIsNotNone(post.post_datetime)
        # ImageField returns an object even when no image is set
        self.assertFalse(post.image)
    
    def test_post_without_header(self):
        """Test post creation without header"""
        post = Post.objects.create(
            post_text='Post without header',
            user=self.user
        )
        
        self.assertIsNone(post.header)
        self.assertEqual(str(post), 'Untitled Post')
    
    def test_post_string_representation(self):
        """Test post string representation"""
        self.assertEqual(str(self.post), 'Test Post')
        
        # Test untitled post
        untitled_post = Post.objects.create(
            post_text='Untitled post content',
            user=self.user
        )
        self.assertEqual(str(untitled_post), 'Untitled Post')
    
    def test_post_like_count_property(self):
        """Test post like count property"""
        # Initially no likes
        self.assertEqual(self.post.like_count, 0)
        
        # Add a like
        PostLike.objects.create(post=self.post, user=self.user)
        self.assertEqual(self.post.like_count, 1)
        
        # Add another like from different user
        another_user = Account.objects.create_user(
            email='another@example.com',
            username='anotheruser',
            first_name='Another',
            last_name='User',
            phone='0987654321',
            password='anotherpass123'
        )
        PostLike.objects.create(post=self.post, user=another_user)
        self.assertEqual(self.post.like_count, 2)
    
    def test_comment_creation(self):
        """Test comment creation"""
        comment = Comment.objects.create(
            post=self.post,
            user=self.user,
            comment_text='Another test comment'
        )
        
        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.comment_text, 'Another test comment')
        self.assertIsNotNone(comment.comment_datetime)
    
    def test_comment_string_representation(self):
        """Test comment string representation"""
        self.assertIn('Comment by testuser on Test Post', str(self.comment))
        
        # Test comment on untitled post
        untitled_post = Post.objects.create(
            post_text='Untitled post content',
            user=self.user
        )
        comment_on_untitled = Comment.objects.create(
            post=untitled_post,
            user=self.user,
            comment_text='Comment on untitled post'
        )
        self.assertIn('Comment by testuser on Untitled Post', str(comment_on_untitled))
    
    def test_comment_like_count_property(self):
        """Test comment like count property"""
        # Initially no likes
        self.assertEqual(self.comment.like_count, 0)
        
        # Add a like
        CommentLike.objects.create(comment=self.comment, user=self.user)
        self.assertEqual(self.comment.like_count, 1)
    
    def test_post_like_creation(self):
        """Test post like creation"""
        post_like = PostLike.objects.create(
            post=self.post,
            user=self.user
        )
        
        self.assertEqual(post_like.post, self.post)
        self.assertEqual(post_like.user, self.user)
    
    def test_post_like_unique_constraint(self):
        """Test post like unique constraint"""
        # First like should work
        PostLike.objects.create(post=self.post, user=self.user)
        
        # Second like from same user should fail
        with self.assertRaises(IntegrityError):
            PostLike.objects.create(post=self.post, user=self.user)
    
    def test_comment_like_creation(self):
        """Test comment like creation"""
        comment_like = CommentLike.objects.create(
            comment=self.comment,
            user=self.user
        )
        
        self.assertEqual(comment_like.comment, self.comment)
        self.assertEqual(comment_like.user, self.user)
    
    def test_comment_like_unique_constraint(self):
        """Test comment like unique constraint"""
        # First like should work
        CommentLike.objects.create(comment=self.comment, user=self.user)
        
        # Second like from same user should fail
        with self.assertRaises(IntegrityError):
            CommentLike.objects.create(comment=self.comment, user=self.user)
    
    def test_post_like_string_representation(self):
        """Test post like string representation"""
        post_like = PostLike.objects.create(post=self.post, user=self.user)
        self.assertIn('testuser likes Test Post', str(post_like))
        
        # Test like on untitled post
        untitled_post = Post.objects.create(
            post_text='Untitled post content',
            user=self.user
        )
        like_on_untitled = PostLike.objects.create(
            post=untitled_post,
            user=self.user
        )
        self.assertIn('testuser likes an Untitled Post', str(like_on_untitled))
    
    def test_comment_like_string_representation(self):
        """Test comment like string representation"""
        comment_like = CommentLike.objects.create(comment=self.comment, user=self.user)
        self.assertIn('testuser likes a comment on Test Post', str(comment_like))
    
    def test_post_user_relationship(self):
        """Test post-user relationship"""
        self.assertEqual(self.post.user, self.user)
        self.assertIn(self.post, self.user.posts.all())
    
    def test_comment_user_relationship(self):
        """Test comment-user relationship"""
        self.assertEqual(self.comment.user, self.user)
        self.assertIn(self.comment, self.user.comments.all())
    
    def test_post_comment_relationship(self):
        """Test post-comment relationship"""
        self.assertIn(self.comment, self.post.comments.all())
    
    def test_post_like_user_relationship(self):
        """Test post like-user relationship"""
        post_like = PostLike.objects.create(post=self.post, user=self.user)
        self.assertIn(post_like, self.user.post_likes.all())
    
    def test_comment_like_user_relationship(self):
        """Test comment like-user relationship"""
        comment_like = CommentLike.objects.create(comment=self.comment, user=self.user)
        self.assertIn(comment_like, self.user.comment_likes.all())
    
    def test_post_datetime_auto_now_add(self):
        """Test post datetime is automatically set"""
        before_creation = timezone.now()
        post = Post.objects.create(
            post_text='Test post for datetime',
            user=self.user
        )
        after_creation = timezone.now()
        
        self.assertGreaterEqual(post.post_datetime, before_creation)
        self.assertLessEqual(post.post_datetime, after_creation)
    
    def test_comment_datetime_auto_now_add(self):
        """Test comment datetime is automatically set"""
        before_creation = timezone.now()
        comment = Comment.objects.create(
            post=self.post,
            user=self.user,
            comment_text='Test comment for datetime'
        )
        after_creation = timezone.now()
        
        self.assertGreaterEqual(comment.comment_datetime, before_creation)
        self.assertLessEqual(comment.comment_datetime, after_creation)
    
    def test_post_with_image(self):
        """Test post creation with image field"""
        # Note: This test doesn't actually upload a file, just tests the field exists
        post = Post.objects.create(
            header='Post with image',
            post_text='Post content',
            user=self.user,
            image=None  # No actual file upload in test
        )
        
        # ImageField returns an object even when no image is set
        self.assertFalse(post.image)
        # In real usage, you would test with actual file uploads
    
    def test_cascade_delete_post(self):
        """Test that deleting a post cascades to comments and likes"""
        # Create likes and comments
        PostLike.objects.create(post=self.post, user=self.user)
        CommentLike.objects.create(comment=self.comment, user=self.user)
        
        # Delete the post
        self.post.delete()
        
        # Verify everything is deleted
        self.assertEqual(Post.objects.count(), 0)
        self.assertEqual(Comment.objects.count(), 0)
        self.assertEqual(PostLike.objects.count(), 0)
        self.assertEqual(CommentLike.objects.count(), 0)
    
    def test_cascade_delete_user(self):
        """Test that deleting a user cascades to their posts and comments"""
        # Create another user with posts and comments
        another_user = Account.objects.create_user(
            email='another@example.com',
            username='anotheruser',
            first_name='Another',
            last_name='User',
            phone='0987654321',
            password='anotherpass123'
        )
        
        another_post = Post.objects.create(
            header='Another user post',
            post_text='Another user content',
            user=another_user
        )
        
        another_comment = Comment.objects.create(
            post=another_post,
            user=another_user,
            comment_text='Another user comment'
        )
        
        # Delete the user
        another_user.delete()
        
        # Verify everything is deleted
        self.assertEqual(Post.objects.filter(user=another_user).count(), 0)
        self.assertEqual(Comment.objects.filter(user=another_user).count(), 0)
