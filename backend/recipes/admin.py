from django.contrib import admin
from django.contrib.admin.decorators import register
from django.utils.translation import gettext_lazy as _

from .models import ProductCategory, Ingredient, RecipeIngredients, Recipe, Tag


# Register your models here.
@register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created', 'is_visible', 'sorting',)
    list_editable = ('is_visible', 'sorting',)
    list_filter = ('is_visible',)
    search_fields = ('name',)
    readonly_fields = ('created', 'updated',)
    save_on_top = True

    fieldsets = (
        (_('page params'),
         {'fields': ('name', 'sorting', 'is_visible', 'created', 'updated',)}),
    )


@register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit', 'created', 'sorting',)
    list_editable = ('sorting',)
    list_filter = ('measurement_unit',)
    search_fields = ('name',)
    readonly_fields = ('created',)
    save_on_top = True

    fieldsets = (
        (_('page params'),
         {'fields': ('name', 'measurement_unit', 'sorting', 'created',)}),
    )


class RecipeIngredientsInLines(admin.TabularInline):
    model = RecipeIngredients


@register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'cooking_time', 'is_visible', 'created', 'sorting',)
    list_editable = ('is_visible', 'sorting',)
    list_filter = ('tags',)
    search_fields = ('name',)
    readonly_fields = ('created',)
    save_on_top = True

    fieldsets = (
        (_('page params'),
         {'fields': (('name', 'cooking_time', 'author',),
                     ('tags',),
                     ('text', 'image',),
                     ('is_visible',),
                     ('sorting', 'created',))
          }),
    )
    inlines = (RecipeIngredientsInLines,)


@register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'is_visible', 'created', 'sorting',)
    list_editable = ('color', 'is_visible', 'sorting',)
    list_filter = ('is_visible',)
    search_fields = ('name',)
    readonly_fields = ('created',)
    save_on_top = True

    fieldsets = (
        (_('page params'),
         {'fields': (('name', 'color',),
                     ('is_visible',),
                     ('sorting', 'created', ))
          }),
    )
