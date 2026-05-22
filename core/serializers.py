from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from typing import Dict, Any

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user model"""
    
    class Meta:
        model = User
        fields = ('id', 'username', 'full_name', 'date_joined')
        read_only_fields = ('id', 'date_joined')


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = ('username', 'full_name', 'password', 'password_confirm')
    
    def validate_username(self, value: str) -> str:
        """Validate username"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                _('A user with that username already exists.')
            )
        
        if len(value) < 3:
            raise serializers.ValidationError(
                _('Username must be at least 3 characters long.')
            )
        
        return value
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that passwords match"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': _('Passwords do not match')
            })
        return attrs
    
    def create(self, validated_data: Dict[str, Any]) -> User:
        """Create a new user"""
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    
    username = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate user credentials"""
        username = attrs.get('username')
        password = attrs.get('password')
        
        user = authenticate(
            request=self.context.get('request'),
            username=username,
            password=password
        )
        
        if not user:
            raise serializers.ValidationError(
                _('Invalid username or password'),
                code='authorization'
            )
        
        if not user.is_active:
            raise serializers.ValidationError(
                _('User account is disabled'),
                code='authorization'
            )
        
        attrs['user'] = user
        return attrs


class RefreshTokenSerializer(serializers.Serializer):
    """Serializer for refreshing access token"""
    
    refresh = serializers.CharField(required=True)
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and generate new access token"""
        refresh = attrs.get('refresh')
        
        try:
            token = RefreshToken(refresh)
            attrs['access'] = str(token.access_token)
        except TokenError:
            raise serializers.ValidationError(
                _('Invalid or expired refresh token'),
                code='token_invalid'
            )
        
        return attrs


class LogoutSerializer(serializers.Serializer):
    """Serializer for user logout"""
    
    refresh = serializers.CharField(required=True)
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate refresh token for blacklisting"""
        refresh = attrs.get('refresh')
        
        try:
            token = RefreshToken(refresh)
            token.blacklist()
        except TokenError:
            raise serializers.ValidationError(
                _('Invalid or expired refresh token'),
                code='token_invalid'
            )
        
        return attrs


class PasswordResetSerializer(serializers.Serializer):
    """Serializer for password reset (without email)"""
    
    username = serializers.CharField(required=True)
    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password],
        write_only=True,
        style={'input_type': 'password'}
    )
    confirm_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate password reset request"""
        username = attrs.get('username')
        old_password = attrs.get('old_password')
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')
        
        # Check if passwords match
        if new_password != confirm_password:
            raise serializers.ValidationError({
                'confirm_password': _('New passwords do not match')
            })
        
        # Check if user exists
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError({
                'username': _('User not found')
            })
        
        # Check old password
        if not user.check_password(old_password):
            raise serializers.ValidationError({
                'old_password': _('Old password is incorrect')
            })
        
        attrs['user'] = user
        return attrs
    
    def save(self) -> User:
        """Reset user password"""
        user = self.validated_data['user']
        new_password = self.validated_data['new_password']
        
        user.set_password(new_password)
        user.save()
        
        return user