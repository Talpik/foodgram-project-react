from django.db import models
from django.contrib.auth.models import AbstractUser

from .managers import AppUserManager


class AppUser(AbstractUser):
    """
    The foodgram app user model, which is used to register with the app.
    """
    email = models.EmailField(
        unique=True,
        max_length=254,
        verbose_name="email"
    )
    username = models.CharField(
        unique=True,
        max_length=100,
        verbose_name="nickname"
    )
    first_name = models.CharField(
        max_length=100,
        verbose_name="first name"
    )
    last_name = models.CharField(
        max_length=100,
        verbose_name="last name"
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ("first_name", "last_name", "username")
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    objects = AppUserManager()

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
        app_label = "users"

    def __str__(self):
        return self.username

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True
