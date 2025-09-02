from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.core.validators import RegexValidator
from utils.validators import validate_phone_number, validate_username

class AccountManager(BaseUserManager):
    def create_user(self, email, username, first_name, last_name, phone, password=None, **kwargs):
        if not email:
            raise ValueError("Email is required")

        if not username:
            raise ValueError("Username is required")

        if not first_name:
            raise ValueError("First name is required")

        if not last_name:
            raise ValueError("Last name is required")

        if not phone:
            raise ValueError("Phone number is required")

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
            phone=phone,  # Include phone in user creation
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, username, first_name, last_name, phone, password, **kwargs):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
            phone=phone,  # Include phone in superuser creation
            password=password
        )

        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class Account(AbstractBaseUser):
    email = models.EmailField(
        null=False, 
        blank=False, 
        unique=True,
        help_text="User's email address"
    )
    username = models.CharField(
        max_length=50, 
        blank=False, 
        null=False,
        validators=[validate_username],
        help_text="Username (3-50 characters, letters, numbers, and underscores only)"
    )
    first_name = models.CharField(
        max_length=30, 
        blank=False, 
        null=False,
        help_text="User's first name"
    )
    last_name = models.CharField(
        max_length=30, 
        blank=False, 
        null=False,
        help_text="User's last name"
    )
    phone = models.CharField(
        max_length=15, 
        blank=False, 
        null=False,
        validators=[validate_phone_number],
        help_text="Phone number in Thai format"
    )

    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = AccountManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name", "phone"]  # Add phone to required fields

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin

    @property
    def full_name(self):
        """Return user's full name."""
        return f"{self.first_name} {self.last_name}".strip()

    class Meta:
        db_table = 'accounts'
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'
        ordering = ['-created_at']
