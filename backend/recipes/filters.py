import django_filters as f

from .models import Ingredient, Recipe, User


class IngredientFilter(f.FilterSet):
    """
    Custom filter for Ingredient model filtered by name field.
    """
    name = f.CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name', 'measurement_unit')


class RecipeFilter(f.FilterSet):
    """
    Custom filter for Recipe model filtered by name and author fields.
    """
    tags = f.AllValuesFilter(
        field_name='tags__slug'
    )
    author = f.ModelChoiceFilter(
        queryset=User.objects.all()
    )

    class Meta:
        model = Recipe
        fields = ['tags', 'author']
