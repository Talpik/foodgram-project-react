import django_filters as f

from .models import Ingredient, Recipe, User


class IngredientFilter(f.FilterSet):
    name = f.CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name', 'measurement_unit')


class RecipeFilter(f.FilterSet):
    tag = f.AllValuesFilter(
        field_name='tag__slug'
    )
    author = f.ModelChoiceFilter(
        queryset=User.objects.all()
    )

    class Meta:
        model = Recipe
        fields = ['tags', 'author']
