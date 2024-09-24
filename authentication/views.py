from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import AccessToken
from django.middleware.csrf import get_token
from .serializers import RegisterSerializer, LoginSerializer

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
            httponly=True,   # Make the cookie HTTP-only
            secure=True,     # Set to True in production
            samesite='Lax',  # Prevent CSRF
            max_age=1800     # Cookie expiry (30 minutes)
        )

        return response

# Check User View
# class CheckUserView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         return Response({
#             'is_authenticated': True,
#             'username': request.user.username,
#             'first_name': request.user.first_name,
#             'last_name': request.user.last_name
#         })

# CSRF Token View
from rest_framework.decorators import api_view

@api_view(['GET'])
def get_csrf_token(request):
    # Create a response object
    response = Response({"message": "Set CSRF cookie"})
    # Get and set CSRF token
    csrf_token = get_token(request)
    response["X-CSRFToken"] = csrf_token
    return response
