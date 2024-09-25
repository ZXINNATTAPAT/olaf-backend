from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import AccessToken
from .serializers import RegisterSerializer, LoginSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import authenticate, login
from django.middleware.csrf import get_token
from django.conf import settings
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView



# Registration View
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

# Login View
class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # Create JWT token
        token = AccessToken.for_user(user)
        # logger.info(f'User {user.username} logged in successfully. Token: {token}')

        # Create response
        response = Response({
            'user_id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone': user.phone,
            'email': user.email,
            'message': 'Login successful'
        }, status=status.HTTP_200_OK)

        # Set cookie with JWT token
        response.set_cookie(
            key='access_token',
            value=str(token),
            httponly=True,
            secure=False,  # Change to True in production
            samesite='None',
            max_age=1800
        )

        # logger.info('Setting access_token cookie successfully.')
        
        return response




class CustomTokenObtainPairView(TokenObtainPairView):
    
    def post(self, request: Request, *args, **kwargs) -> Response:
        
        response = super().post(request, *args, **kwargs)
        
        access_token = response.data["access"]
        
        response.set_cookie(
            key=settings.SIMPLE_JWT["AUTH_COOKIE"],
            value=access_token,
            domain=settings.SIMPLE_JWT["AUTH_COOKIE_DOMAIN"],
            path=settings.SIMPLE_JWT["AUTH_COOKIE_PATH"],
            expires=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
            secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
            httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
            samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
        )
        
        return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Check if user is authenticated
def check_authentication(request):
    if request.user.is_authenticated:
        # logger.info(f'User {request.user.username} is authenticated.')
        return Response({
            "authenticated": True,
            "user_id": request.user.id,
            "username": request.user.username,
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "email": request.user.email,
        }, status=status.HTTP_200_OK)
    else:
        # logger.warning('User is not authenticated.')
        return Response({"authenticated": False}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def get_csrf_token(request):
    response = Response({"message": "Set CSRF cookie"})
    response["X-CSRFToken"] = get_token(request)
    return response

@api_view(['POST'])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)

    if user:
        # Call the LoginView logic to handle JWT and cookie setting
        login(request, user)  # Only needed if you plan to use session authentication
        token = AccessToken.for_user(user)
        response = Response({
            'message': 'User logged in',
            'user_id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone': user.phone,
            'email': user.email,
            'access_token': str(token)
        }, status=status.HTTP_200_OK)
        
        # Set cookie with JWT token
        response.set_cookie(
            key='access_token',
            value=str(token),
            httponly=True,
            secure=False,
            samesite='Lax',
            max_age=1800
        )

        print(f'Setting access_token cookie: {token}')
        return response
    else:
        return Response({'message': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)
