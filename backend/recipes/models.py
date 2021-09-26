from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404

from .common_fields import FieldSlug, FieldVisible, FieldUpdated, FieldSorting, \
    FieldCreated, FieldImage


User = get_user_model()


class ProductCategory(FieldSlug, FieldVisible, FieldUpdated, FieldCreated, FieldSorting):
    name = models.CharField(
        max_length=100,
        verbose_name=_('name of the product category'),  # Название категории продуктов
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
    name = models.CharField(
        max_length=100,
        verbose_name=_('name of the ingredient'),  # Название ингидиента
        blank=False,
        db_index=True
    )
    measurement_unit = models.CharField(
        max_length=20,
        verbose_name=_('unit of measurement')  # единица измерения
    )
    # category = models.ForeignKey(
    #     ProductCategory,
    #     on_delete=models.CASCADE,
    #     blank=True
    # )

    class Meta:
        verbose_name = _('ingredient')
        verbose_name_plural = _('ingredients')
        app_label = 'recipes'
        ordering = ('sorting',)

    def __str__(self):
        return self.name


class Tag(FieldSlug, FieldVisible, FieldCreated, FieldSorting):
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


class Recipe(FieldSlug, FieldImage, FieldVisible, FieldUpdated, FieldCreated, FieldSorting):
    name = models.CharField(
        max_length=100,
        verbose_name=_('name of the recipe'),  # Название рецепта
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
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredients = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(
        verbose_name=_('quantity')  # количество
    )

    class Meta:
        verbose_name = _('ingredients of recipe')  # список ингедиентов
        verbose_name_plural = _('ingredients of recipe')
        app_label = 'recipes'

    def add_ingredient(self, recipe_id, name, quantity):
        ingredient = get_object_or_404(Ingredient, name=name)
        return self.objects.get_or_create(
            recipe_id=recipe_id,
            ingredient=ingredient,
            quantity=quantity
        )
