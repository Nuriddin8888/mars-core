from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from typing import Dict, Any

from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    RefreshTokenSerializer,
    LogoutSerializer,
    UserSerializer,
    PasswordResetSerializer,
)

User = get_user_model()
    

class RegisterView(generics.CreateAPIView):
    """User registration endpoint"""
    
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs) -> Response:
        """Register a new user and return tokens"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.save()
        
        # Generate tokens for the new user
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """User login endpoint"""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs) -> Response:
        """Authenticate user and return tokens"""
        serializer = LoginSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_200_OK)


class RefreshTokenView(APIView):
    """Refresh access token endpoint"""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs) -> Response:
        """Generate new access token using refresh token"""
        serializer = RefreshTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        return Response({
            'access': serializer.validated_data['access']
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """User logout endpoint"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs) -> Response:
        """Blacklist refresh token for logout"""
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        return Response({
            'message': 'Successfully logged out'
        }, status=status.HTTP_200_OK)


class ProtectedView(APIView):
    """Example protected endpoint"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs) -> Response:
        """Access only with valid JWT token"""
        return Response({
            'message': 'You have access to protected data!',
            'user': UserSerializer(request.user).data,
            'data': {
                'secret_info': 'This is protected content',
                'timestamp': '2026-05-22 12:00:00'
            }
        }, status=status.HTTP_200_OK)


class ProfileView(generics.RetrieveUpdateAPIView):
    """User profile management endpoint"""
    
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Return current authenticated user"""
        return self.request.user


class PasswordResetView(APIView):
    """Password reset endpoint (without email)"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs) -> Response:
        """Reset user password with old password verification"""
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        serializer.save()
        
        return Response({
            'message': 'Password has been reset successfully'
        }, status=status.HTTP_200_OK)