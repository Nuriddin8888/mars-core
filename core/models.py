from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from typing import Optional


class UserManager(BaseUserManager):
    """Custom user manager for username-based authentication"""
    
    def create_user(
        self,
        username: str,
        password: Optional[str] = None,
        **extra_fields
    ) -> 'User':
        """Create and save a regular user"""
        if not username:
            raise ValueError(_('Username must be provided'))
        
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(
        self,
        username: str,
        password: Optional[str] = None,
        **extra_fields
    ) -> 'User':
        """Create and save a superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True'))
        
        return self.create_user(username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model with username as unique identifier (no email)"""
    
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        db_index=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.')
    )
    
    full_name = models.CharField(
        _('full name'),
        max_length=255,
        blank=True
    )
    
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_('Designates whether this user should be treated as active')
    )
    
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site')
    )
    
    date_joined = models.DateTimeField(
        _('date joined'),
        default=timezone.now
    )
    
    last_login = models.DateTimeField(
        _('last login'),
        blank=True,
        null=True
    )
    
    objects = UserManager()
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []  # email talab qilinmaydi
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        db_table = 'core_user'
        ordering = ['-date_joined']
    
    def __str__(self) -> str:
        return self.username
    
    def get_full_name(self) -> str:
        """Return the full name of the user"""
        return self.full_name or self.username
    
    def get_short_name(self) -> str:
        """Return the short name of the user"""
        return self.username