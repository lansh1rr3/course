from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('manager', 'Manager'),
    )
    email = models.EmailField(_('email address'), unique=True)
    is_email_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    # Новые поля
    avatar = models.ImageField(_('avatar'), upload_to='avatars/', null=True, blank=True)
    phone_number = models.CharField(_('phone number'), max_length=15, null=True, blank=True)
    country = models.CharField(_('country'), max_length=100, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def is_manager(self):
        return self.role == 'manager'

    def is_user(self):
        return self.role == 'user'
