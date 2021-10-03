from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404

from .common_fields import FieldSlug, FieldVisible, FieldUpdated, \
    FieldSorting, FieldCreated, FieldImage


User = get_user_model()


class ProductCategory(FieldSlug, FieldVisible, FieldUpdated,
                      FieldCreated, FieldSorting):
    """
    Model for registering a product category.
    This is the groundwork for a future feature
    of dividing the shopping list into categories.
    """
    name = models.CharField(
        max_length=100,
        verbose_name=_('name of the product category'),
        blank=False,
    )

    class Meta:
        verbose_name = _('category of products')
        verbose_name_plural = _('categories of products')
        app_label = 'recipes'
        ordering = ('sorting',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('page', kwargs={'slug': self.slug})


class Ingredient(FieldCreated, FieldSorting):
    """
    Food Ingredient Model with Name and Unit.
    """
    name = models.CharField(
        max_length=100,
        verbose_name=_('name of the ingredient'),
        blank=False,
        db_index=True
    )
    measurement_unit = models.CharField(
        max_length=20,
        verbose_name=_('unit of measurement')
    )

    class Meta:
        verbose_name = _('ingredient')
        verbose_name_plural = _('ingredients')
        app_label = 'recipes'
        ordering = ('sorting',)

    def __str__(self):
        return self.name


class Tag(FieldSlug, FieldVisible, FieldCreated, FieldSorting):
    """
    Tag model - which allows you to register
    the recommended consumption time of the dish.
    Having a special hex color code for frontend.
    """
    MEAL_TIME = (
        ('breakfast', 'Завтрак'),
        ('lunch', 'Обед'),
        ('dinner', 'Ужин'),
    )
    name = models.CharField(
        max_length=20,
        verbose_name=_('meal time'),
        choices=MEAL_TIME,
        blank=False,
        db_index=True
    )
    color = models.CharField(
        max_length=10,
        verbose_name=_('HEX color scheme'),
        blank=False
    )

    class Meta:
        verbose_name = _('tag')
        verbose_name_plural = _('tags')
        app_label = 'recipes'
        ordering = ('sorting',)

    def __str__(self):
        return self.name


class Recipe(FieldSlug, FieldImage, FieldVisible,
             FieldUpdated, FieldCreated, FieldSorting):
    """
    The main application model that stores
    aggregated information about a food recipe.
    The model is associated with user models,
    time tags, and food ingredients.
    """
    name = models.CharField(
        max_length=100,
        verbose_name=_('name of the recipe'),
        blank=False,
        db_index=True
    )
    author = models.ForeignKey(
        User,
        blank=True,
        on_delete=models.CASCADE,
        related_name="recipes"
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name=_('tags'),
        related_name="recipes"
    )
    text = models.TextField(
        verbose_name=_('text'),
        null=True,
        blank=True
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='RecipeIngredients',
        verbose_name=_('ingredients of recipe'),  # список ингедиентов
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name=_('cooking time'),
        # cooking time cannot be less than 1 minute
        validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = _('recipe')
        verbose_name_plural = _('recipes')
        app_label = 'recipes'
        ordering = ('sorting',)

    def __str__(self):
        return self.name


class RecipeIngredients(models.Model):
    """
    Helpful model that stores the association
    of a specific recipe and a specific ingredient
    and its amount.
    """
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='recipe',
        related_name='ingredients_amounts',
    )
    ingredients = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredients_amounts',)
    amount = models.PositiveIntegerField(verbose_name=_('amount'))

    class Meta:
        verbose_name = _('ingredients of recipe')
        verbose_name_plural = _('ingredients of recipe')
        app_label = 'recipes'
        unique_together = ('ingredients', 'recipe')
        constraints = [
            models.UniqueConstraint(
                fields=['ingredients', 'recipe'],
                name='recipe_ingredients_unique',
            )
        ]

    def add_ingredient(self, recipe_id, name, amount):
        """
        Function of adding an ingredient and its quantity to a recipe.

        Args:
            recipe_id: ID of the recipe.
            name: Name of the ingredient.
            amount: Amount of the ingredient.

        Returns:
            RecipeIngredients instance.

        """
        ingredient = get_object_or_404(Ingredient, name=name)
        return self.objects.get_or_create(
            recipe_id=recipe_id,
            ingredient=ingredient,
            amount=amount
        )


class Subscription(FieldCreated):
    """
    User subscription model for author's recipes.
    """
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
    """
    Model for storing selected recipes for a specific user.
    """
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
        app_label = 'recipes'

    def __str__(self):
        return f"Recipe {self.recipe} in favorites list of {self.user}"


class ShoppingList(FieldCreated):
    """
    Model for storing recipes in a shopping list,
    which will allow you to aggregate products into a single list.
    """
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
