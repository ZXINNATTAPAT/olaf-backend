from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from authentication.models import Account, AccountManager
from django.contrib.auth import authenticate
from datetime import timedelta

class AccountModelTest(TestCase):
    """Test cases for Account model"""
    
    def setUp(self):
        """Set up test data"""
        self.valid_user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'phone': '1234567890',
            'password': 'testpass123'
        }
    
    def test_create_user_success(self):
        """Test successful user creation"""
        user = Account.objects.create_user(**self.valid_user_data)
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')
        self.assertEqual(user.phone, '1234567890')
        self.assertTrue(user.check_password('testpass123'))
        self.assertFalse(user.is_admin)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_create_user_missing_email(self):
        """Test user creation fails without email"""
        data = self.valid_user_data.copy()
        del data['email']
        with self.assertRaises(TypeError):
            Account.objects.create_user(**data)
    
    def test_create_user_missing_username(self):
        """Test user creation fails without username"""
        data = self.valid_user_data.copy()
        del data['username']
        with self.assertRaises(TypeError):
            Account.objects.create_user(**data)
    
    def test_create_user_missing_first_name(self):
        """Test user creation fails without first name"""
        data = self.valid_user_data.copy()
        del data['first_name']
        with self.assertRaises(TypeError):
            Account.objects.create_user(**data)
    
    def test_create_user_missing_last_name(self):
        """Test user creation fails without last name"""
        data = self.valid_user_data.copy()
        del data['last_name']
        with self.assertRaises(TypeError):
            Account.objects.create_user(**data)
    
    def test_create_user_missing_phone(self):
        """Test user creation fails without phone"""
        data = self.valid_user_data.copy()
        del data['phone']
        with self.assertRaises(TypeError):
            Account.objects.create_user(**data)
    
    def test_create_superuser_success(self):
        """Test successful superuser creation"""
        user = Account.objects.create_superuser(**self.valid_user_data)
        self.assertTrue(user.is_admin)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)
    
    def test_user_string_representation(self):
        """Test user string representation"""
        user = Account.objects.create_user(**self.valid_user_data)
        self.assertEqual(str(user), 'testuser')
    
    def test_user_permissions(self):
        """Test user permission methods"""
        user = Account.objects.create_user(**self.valid_user_data)
        self.assertTrue(user.has_perm('auth.add_user'))
        self.assertTrue(user.has_module_perms('auth'))
    
    def test_user_authentication(self):
        """Test user authentication with Django's authenticate function"""
        user = Account.objects.create_user(**self.valid_user_data)
        authenticated_user = authenticate(email='test@example.com', password='testpass123')
        self.assertEqual(authenticated_user, user)
    
    def test_user_authentication_wrong_password(self):
        """Test user authentication fails with wrong password"""
        user = Account.objects.create_user(**self.valid_user_data)
        authenticated_user = authenticate(email='test@example.com', password='wrongpass')
        self.assertIsNone(authenticated_user)
    
    def test_user_authentication_wrong_email(self):
        """Test user authentication fails with wrong email"""
        user = Account.objects.create_user(**self.valid_user_data)
        authenticated_user = authenticate(email='wrong@example.com', password='testpass123')
        self.assertIsNone(authenticated_user)
    
    def test_email_normalization(self):
        """Test email normalization during user creation"""
        data = self.valid_user_data.copy()
        data['email'] = 'TEST@EXAMPLE.COM'
        user = Account.objects.create_user(**data)
        # Django's normalize_email only changes domain case, not local part
        self.assertEqual(user.email, 'TEST@example.com')
    
    def test_unique_email_constraint(self):
        """Test email uniqueness constraint"""
        Account.objects.create_user(**self.valid_user_data)
        with self.assertRaises(IntegrityError):
            Account.objects.create_user(**self.valid_user_data)
    
    def test_required_fields(self):
        """Test required fields configuration"""
        self.assertEqual(Account.USERNAME_FIELD, 'email')
        self.assertEqual(Account.REQUIRED_FIELDS, ['username', 'first_name', 'last_name', 'phone'])
    
    def test_user_timestamps(self):
        """Test user creation and update timestamps"""
        user = Account.objects.create_user(**self.valid_user_data)
        self.assertIsNotNone(user.created_at)
        self.assertIsNotNone(user.updated_at)
        # Timestamps might be slightly different due to microsecond precision
        time_diff = abs(user.updated_at - user.created_at)
        self.assertLessEqual(time_diff, timedelta(seconds=1))
    
    def test_user_update_timestamp(self):
        """Test user update timestamp changes on save"""
        user = Account.objects.create_user(**self.valid_user_data)
        original_updated_at = user.updated_at
        user.first_name = 'Updated'
        user.save()
        self.assertGreater(user.updated_at, original_updated_at)
