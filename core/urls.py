from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/refresh/', views.RefreshTokenView.as_view(), name='token_refresh'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    
    # Password reset endpoint (without email)
    path('auth/password-reset/', views.PasswordResetView.as_view(), name='password_reset'),
    
    # Protected endpoints
    path('protected/', views.ProtectedView.as_view(), name='protected'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
]