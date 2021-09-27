from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from .managers import AppUserManager


class AppUser(AbstractUser):
    email = models.EmailField(
        unique=True,
        max_length=254,
        verbose_name=_('email')
    )
    username = models.CharField(
        unique=True,
        max_length=100,
        verbose_name=_('nickname')
    )
    first_name = models.CharField(
        max_length=100,
        verbose_name=_('first name')
    )
    last_name = models.CharField(
        max_length=100,
        verbose_name=_('last name')
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('first_name', 'last_name', 'username')
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    objects = AppUserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        app_label = 'users'

    def __str__(self):
        return self.username

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True
