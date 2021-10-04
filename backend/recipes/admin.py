from django.contrib import admin
from django.contrib.admin.decorators import register
from .models import ProductCategory, Ingredient, RecipeIngredient, Recipe, Tag


@register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    """
    Registering the required fields
    of the Product Category model in the Django admin panel.

    Note:
        It's for next futures.

    """
    list_display = ("name", "created", "is_visible", "sorting",)
    list_editable = ("is_visible", "sorting",)
    list_filter = ("is_visible",)
    search_fields = ("name",)
    readonly_fields = ("created", "updated",)
    save_on_top = True

    fieldsets = (
        ("page params",
         {"fields": ("name", "sorting", "is_visible", "created", "updated",)}),
    )


@register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """
    Registering the required fields
    of the Ingredient model in the Django admin panel.

    """
    list_display = ('name', 'measurement_unit', 'created', 'sorting',)
    list_editable = ('sorting',)
    list_filter = ('measurement_unit',)
    search_fields = ('name',)
    readonly_fields = ('created',)
    save_on_top = True

    fieldsets = (
        ("page params",
         {"fields": ("name", "measurement_unit", "sorting", "created",)}),
    )


class RecipeIngredientsInLines(admin.TabularInline):
    """
    Integration model with ingredients for Recipes.

    """
    model = RecipeIngredient


@register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """
    Registering the required fields
    of the Recipe model in the Django admin panel.

    """
    list_display = ("name", "cooking_time", "is_visible", "created", "sorting",)
    list_editable = ("is_visible", "sorting",)
    list_filter = ("tags",)
    search_fields = ("name",)
    readonly_fields = ("created",)
    save_on_top = True

    fieldsets = (
        ("page params",
         {"fields": (("name", "cooking_time", "author",),
                     ("tags",),
                     ("text", "image",),
                     ("is_visible",),
                     ("sorting", "created",))
          }),
    )
    inlines = (RecipeIngredientsInLines,)


@register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Registering the required fields
    of the Tag model in the Django admin panel.

    """
    list_display = ("name", "color", "is_visible", "created", "sorting",)
    list_editable = ("color", "is_visible", "sorting",)
    list_filter = ("is_visible",)
    search_fields = ("name",)
    readonly_fields = ("created",)
    save_on_top = True

    fieldsets = (
        ("page params",
         {"fields": (("name", "color",),
                     ("is_visible",),
                     ("sorting", "created", ))
          }),
    )
