from django.http.response import HttpResponse

from djoser.views import UserViewSet

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from .filters import IngredientFilter, RecipeFilter
from .models import (User, Ingredient, Tag, Recipe,
                     Subscription, FavoriteRecipe, ShoppingList)
from .permissions import IsOwnerOrAdminOrReadOnly
from .serializers import (UserSerializer, IngredientSerializer,
                          TagSerializer, RecipeSerializer,
                          SubscriptionSerializer, FavoriteRecipeSerializer,
                          ShoppingListSerializer, SubscriptionsSerializer)


class AppPagination(PageNumberPagination):
    page_size_query_param = "limit"


class AppUserViewSet(UserViewSet):
    """
    Viewer class with methods for url
    'users/subscribe', 'users/delete_subscribe', 'users/subscriptions'.

    """
    serializer_class = UserSerializer
    permission_classes = (IsOwnerOrAdminOrReadOnly,)
    pagination_class = AppPagination
    queryset = User.objects.all()

    @action(detail=True, permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)

        data = {
            'user': user.id,
            'author': author.id,
        }
        serializer = SubscriptionSerializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)
        subscription = get_object_or_404(
            Subscription, user=user, author=author
        )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        queryset = Subscription.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionsSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Viewer class for url 'tags'.

    """
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    queryset = Tag.objects.all()


class IngredientsViewSet(viewsets.ModelViewSet):
    """
    Viewer class for url 'ingredients'.

    """
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filterset_class = IngredientFilter
    queryset = Ingredient.objects.all()


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Main viewer class with methods for url
    'recipes/', 'recipes/favorite', 'recipes/delete_favorite' and others.

    """
    serializer_class = RecipeSerializer
    permission_classes = (IsOwnerOrAdminOrReadOnly,)
    pagination_class = AppPagination
    filter_class = RecipeFilter
    queryset = Recipe.objects.all()

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    def get_queryset(self):
        queryset = self.filter_class.filter_recipe_queryset(self.request)
        return queryset

    @action(detail=True, permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)

        data = {
            'user': user.id,
            'recipe': recipe.id,
        }
        serializer = FavoriteRecipeSerializer(
            data=data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        favorite_recipe = get_object_or_404(
            FavoriteRecipe, user=user, recipe=recipe
        )
        favorite_recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)

        data = {
            'user': user.id,
            'recipe': recipe.id,
        }
        serializer = ShoppingListSerializer(
            data=data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        favorites = get_object_or_404(
            ShoppingList, user=user, recipe=recipe
        )
        favorites.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        all_recipes = Recipe.objects.all()
        recipes = all_recipes.shopping_list_recipes.filter(
            user=request.user
        )
        value_list = recipes.objects.value_list(
            "ingredients__ingredients__name",
            "ingredients__amount",
            "ingredients__ingredients_measurement__unit",
        )

        shop_dict = dict()
        for e in value_list:
            if not shop_dict.get(f"{e[0]}, {e[2]} - "):
                shop_dict[f"{e[0]}, {e[2]} : "] = 0
                shop_dict[f"{e[0]}, {e[2]} : "] += e[1]
            else:
                shop_dict[f"{e[0]}, {e[2]} : "] += e[1]
        shop_string = "\n".join("{} {},".format(
            k, v
        ) for k, v in shop_dict.items())
        response = HttpResponse(shop_string, "Content-Type: text/plain")
        response["Content-Disposition"] = 'attachment; filename="shoplist.txt"'
        return response
