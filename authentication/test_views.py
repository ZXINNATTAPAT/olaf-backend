from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
import json

Account = get_user_model()

class AuthenticationViewsTest(TestCase):
    """Test cases for authentication views"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'phone': '1234567890',
            'password': 'testpass123'
        }
        self.user = Account.objects.create_user(**self.user_data)
        self.login_data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        self.register_data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'phone': '0987654321',
            'password': 'newpass123'
        }
    
    def test_login_success(self):
        """Test successful login"""
        response = self.client.post('/auth/login/', self.login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)
        self.assertIn('X-CSRFToken', response)
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        invalid_data = {'email': 'test@example.com', 'password': 'wrongpass'}
        response = self.client.post('/auth/login/', invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('Email or Password is incorrect!', str(response.data))
    
    def test_login_missing_email(self):
        """Test login with missing email"""
        invalid_data = {'password': 'testpass123'}
        response = self.client.post('/auth/login/', invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_login_missing_password(self):
        """Test login with missing password"""
        invalid_data = {'email': 'test@example.com'}
        response = self.client.post('/auth/login/', invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_register_success(self):
        """Test successful user registration"""
        response = self.client.post('/auth/register/', self.register_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Registered!', str(response.data))
        
        # Verify user was created
        new_user = Account.objects.get(email='newuser@example.com')
        self.assertEqual(new_user.username, 'newuser')
        self.assertEqual(new_user.first_name, 'New')
        self.assertEqual(new_user.last_name, 'User')
        self.assertEqual(new_user.phone, '0987654321')
    
    def test_register_duplicate_email(self):
        """Test registration with duplicate email"""
        duplicate_data = self.register_data.copy()
        duplicate_data['email'] = 'test@example.com'
        response = self.client.post('/auth/register/', duplicate_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_register_missing_fields(self):
        """Test registration with missing required fields"""
        incomplete_data = {'email': 'incomplete@example.com', 'username': 'incomplete'}
        response = self.client.post('/auth/register/', incomplete_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_logout_success(self):
        """Test successful logout"""
        # First login to get tokens
        login_response = self.client.post('/auth/login/', self.login_data, format='json')
        access_token = login_response.data['access_token']
        refresh_token = login_response.data['refresh_token']
        
        # Set cookies for logout
        self.client.cookies['access'] = access_token
        self.client.cookies['refresh'] = refresh_token
        
        # Test logout
        response = self.client.post('/auth/logout/', HTTP_AUTHORIZATION=f'Bearer {access_token}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_logout_invalid_token(self):
        """Test logout with invalid token"""
        response = self.client.post('/auth/logout/', HTTP_AUTHORIZATION='Bearer invalid_token')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_logout_no_token(self):
        """Test logout without token"""
        response = self.client.post('/auth/logout/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_user_endpoint_authenticated(self):
        """Test user endpoint with valid authentication"""
        # First login to get token
        login_response = self.client.post('/auth/login/', self.login_data, format='json')
        access_token = login_response.data['access_token']
        
        # Test user endpoint
        response = self.client.get('/auth/user/', HTTP_AUTHORIZATION=f'Bearer {access_token}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')
        self.assertEqual(response.data['username'], 'testuser')
    
    def test_user_endpoint_unauthenticated(self):
        """Test user endpoint without authentication"""
        response = self.client.get('/auth/user/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_user_endpoint_invalid_user(self):
        """Test user endpoint with invalid user ID"""
        # Create a token for a user that doesn't exist in database
        fake_user = Account(email='fake@example.com', username='fakeuser')
        fake_user.id = 99999
        refresh = RefreshToken.for_user(fake_user)
        access_token = str(refresh.access_token)
        
        response = self.client.get('/auth/user/', HTTP_AUTHORIZATION=f'Bearer {access_token}')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_token_refresh_success(self):
        """Test token refresh endpoint"""
        # First login to get tokens
        login_response = self.client.post('/auth/login/', self.login_data, format='json')
        refresh_token = login_response.data['refresh_token']
        
        # Set refresh cookie
        self.client.cookies['refresh'] = refresh_token
        
        # Test token refresh
        response = self.client.post('/auth/token/refresh/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
    
    def test_token_refresh_no_cookie(self):
        """Test token refresh without refresh cookie"""
        response = self.client.post('/auth/token/refresh/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_csrf_token_in_response(self):
        """Test that CSRF token is included in login response"""
        response = self.client.post('/auth/login/', self.login_data, format='json')
        self.assertIn('X-CSRFToken', response)
        self.assertIsNotNone(response['X-CSRFToken'])
    
    def test_cookie_settings(self):
        """Test that cookies are set with correct settings"""
        response = self.client.post('/auth/login/', self.login_data, format='json')
        
        # Check access token cookie
        self.assertIn('access', response.cookies)
        access_cookie = response.cookies['access']
        self.assertTrue(access_cookie['httponly'])
        
        # Check refresh token cookie
        self.assertIn('refresh', response.cookies)
        refresh_cookie = response.cookies['refresh']
        self.assertTrue(refresh_cookie['httponly'])
    
    def test_authentication_failed_message(self):
        """Test authentication failed error message"""
        invalid_data = {'email': 'nonexistent@example.com', 'password': 'wrongpass'}
        response = self.client.post('/auth/login/', invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('Email or Password is incorrect!', str(response.data))
    
    def test_register_validation_errors(self):
        """Test registration validation errors"""
        # Test with invalid email format
        invalid_email_data = self.register_data.copy()
        invalid_email_data['email'] = 'invalid-email'
        response = self.client.post('/auth/register/', invalid_email_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test with empty username
        empty_username_data = self.register_data.copy()
        empty_username_data['username'] = ''
        response = self.client.post('/auth/register/', empty_username_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
