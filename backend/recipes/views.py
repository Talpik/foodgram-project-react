from django.db.models import Exists, OuterRef
from django.http.response import HttpResponse

from djoser.views import UserViewSet

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from .filters import IngredientFilter, RecipeFilter
from .models import (User, Ingredient, Tag, Recipe, RecipeIngredient,
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
        queryset = self.filter_class.filter_recipe_queryset()
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
        user = request.user
        shopping_list_owners = user.shopping_list_owners.all()
        shopping_list = dict()
        for item in shopping_list_owners:
            recipe = item.recipe
            ingredients = RecipeIngredient.objects.filter(recipe=recipe)
            for ingredient in ingredients:
                amount = ingredient.amount
                name = ingredient.ingredients.name
                measurement_unit = ingredient.ingredients.measurement_unit
                if name not in shopping_list:
                    shopping_list[name] = {
                        "measurement_unit": measurement_unit,
                        "amount": amount
                    }
                else:
                    shopping_list[name]["amount"] = (
                        shopping_list[name]["amount"] + amount
                    )

        shop_list = []
        for item in shopping_list:
            shop_list.append(f'{item} - {shopping_list[item]["amount"]} '
                             f'{shopping_list[item]["measurement_unit"]} \n')
        response = HttpResponse(shop_list, "Content-Type: text/plain")
        response["Content-Disposition"] = 'attachment; filename="shoplist.txt"'
        return response
