import django_filters as f
from django.db.models import OuterRef, Exists

from .models import Ingredient, Recipe, User, FavoriteRecipe, ShoppingList


class IngredientFilter(f.FilterSet):
    """
    Custom filter for Ingredient model filtered by name field.
    """
    name = f.CharFilter(field_name="name", lookup_expr="istartswith")

    class Meta:
        model = Ingredient
        fields = ("name", "measurement_unit")


class RecipeFilter(f.FilterSet):
    """
    Custom filter for Recipe model filtered by name and author fields.
    """
    tags = f.AllValuesFilter(
        field_name="tags__slug"
    )
    author = f.ModelChoiceFilter(
        queryset=User.objects.all()
    )

    class Meta:
        model = Recipe
        fields = ["tags", "author"]

    @staticmethod
    def filter_recipe_queryset(request):
        user = request.user

        if user.is_anonymous:
            return Recipe.objects.all().order_by("-created")

        queryset = Recipe.objects.annotate(
            is_favorited=Exists(FavoriteRecipe.objects.filter(
                user=user, recipe_id=OuterRef('pk')
            )),
            is_in_shopping_cart=Exists(ShoppingList.objects.filter(
                user=user, recipe_id=OuterRef('pk')
            ))
        ).order_by('-created')

        if request.GET.get('is_favorited'):
            return queryset.filter(
                is_favorited=True).order_by("-created")
        elif request.GET.get('is_in_shopping_cart'):
            return queryset.filter(
                is_in_shopping_cart=True).order_by("-created")
        return queryset
