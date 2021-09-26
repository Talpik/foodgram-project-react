from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from recipes.models import Recipe
from recipes.common_fields import FieldCreated
from .managers import AppUserManager


User = get_user_model()


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
        ordering = ('sorting',)

    def __str__(self):
        return self.username

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True


class Subscription(FieldCreated):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="followers"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipe_authors"
    )

    class Meta:
        verbose_name = _('subscription')
        verbose_name_plural = _('subscriptions')
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='follow_unique'
            )
        ]

    def __str__(self):
        return f'{self.user} subscribed on {self.author}'


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorite_recipe_subscribers"
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorite_recipes"
    )

    class Meta:
        verbose_name = _('favorite recipe')
        verbose_name_plural = _('favorite recipes')
        app_label = 'users'
        ordering = ('sorting',)

    def __str__(self):
        return f"Recipe {self.recipe} in favorites list of {self.user}"


class ShoppingList(FieldCreated):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shopping_list_owners"
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="shopping_list_recipes"
    )

    def __str__(self):
        return f"Recipe {self.recipe} in shopping list of {self.user}"
