from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import Ingredient, Tag, RecipeIngredients, User, Recipe
from .models import Subscription, ShoppingList, FavoriteRecipe


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(user=request.user, author=obj.id).exists()


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredients.id')
    name = serializers.ReadOnlyField(source='ingredients.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit'
    )

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'name', 'amount', 'measurement_unit')


class SubscriptionRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientsSerializer(
        source='ingredients_amounts',
        many=True,
        read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'author', 'tags', 'text', 'ingredients',
                  'cooking_time', 'image', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return FavoriteRecipe.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return ShoppingList.objects.filter(user=request.user, recipe=obj).exists()

    def validate(self, data: dict) -> dict:
        """
        Args:
            data (dict): Dictionary with recipe's data.

        Returns:
            data (dict): Dictionary with recipe's data, in which was added ingredients id's.

        """
        ingredients = self.initial_data.get('ingredients')
        set_ingredients = set()
        for ingredient in ingredients:
            if int(ingredient.get('amount')) <= 0:
                raise serializers.ValidationError(
                    ('Make sure the value of the amount '
                     'ingredient is greater than 0')
                )
            ingredient_id = ingredient.get('id')
            if ingredient_id in set_ingredients:
                raise serializers.ValidationError(
                    'The ingredient in the recipe must not be repeated.'
                )
            set_ingredients.add(ingredient_id)
        data['ingredients'] = ingredients
        return data

    def create(self, data: dict) -> Recipe:
        """
        Args:
            data (dict): Validated data.

        Returns:
            recipe (Recipe): A new instance of recipe.

        """
        image = data.pop('image')
        ingredients = data.pop('ingredients')
        recipe = Recipe.objects.create(image=image, **data)
        tags = self.initial_data.get('tags')

        for tag_id in tags:
            recipe.tags.add(get_object_or_404(Tag, pk=tag_id))

        for ingredient in ingredients:
            RecipeIngredients.objects.create(
                recipe=recipe,
                ingredients_id=ingredient.get('id'),
                amount=ingredient.get('amount')
            )
        return recipe

    def update(self, recipe: Recipe, data: dict) -> Recipe:
        """
        Args:
            recipe (Recipe):
            data (dict):

        Returns:
            recipe (Recipe):

        """
        recipe.tags.clear()
        tags = self.initial_data.get('tags')

        for tag_id in tags:
            recipe.tags.add(get_object_or_404(Tag, pk=tag_id))

        RecipeIngredients.objects.filter(recipe=recipe).delete()
        for ingredient in data.get('ingredients'):
            ingredient_amount = RecipeIngredients.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount')
            )
            ingredient_amount.save()

        if data.get('image') is not None:
            recipe.image = data.get('image')
        recipe.name = data.get('name')
        recipe.text = data.get('text')
        recipe.cooking_time = data.get('cooking_time')
        recipe.save()
        return recipe


class SubscriptionSerializer(serializers.ModelSerializer):
    queryset = User.objects.all()
    user = serializers.PrimaryKeyRelatedField(queryset=queryset)
    author = serializers.PrimaryKeyRelatedField(queryset=queryset)

    class Meta:
        model = Subscription
        fields = ('user', 'author')

    def validate(self, data):
        request = self.context.get('request')
        author_id = data.get('author').id
        subscription_exists = Subscription.objects.filter(
            user=request.user,
            author__id=author_id
        ).exists()

        if request.method == 'GET':
            if request.user.id == author_id:
                raise serializers.ValidationError(
                    "You can't subscribe to yourself"
                )
            if subscription_exists:
                raise serializers.ValidationError(
                    'You are already following this user.'
                )

        return data


class SubscriptionsSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    username = serializers.ReadOnlyField(source='author.username')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'username',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=obj.user, author=obj.author
        ).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = Recipe.objects.filter(author=obj.author)
        if limit is not None:
            queryset = Recipe.objects.filter(
                author=obj.author
            )[:int(limit)]

        return SubscriptionRecipeSerializer(queryset, many=True).data

    @staticmethod
    def get_recipes_count(obj):
        return Recipe.objects.filter(author=obj.author).count()


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = FavoriteRecipe
        fields = ('user', 'recipe')

    def validate(self, data):
        request = self.context.get('request')
        recipe_id = data.get('recipe').id
        favorite_exists = FavoriteRecipe.objects.filter(
            user=request.user,
            recipe__id=recipe_id
        ).exists()

        if request.method == 'GET' and favorite_exists:
            raise serializers.ValidationError(
                'The recipe has already been added to favorites.'
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return SubscriptionRecipeSerializer(
            instance.recipe,
            context=context).data


class ShoppingListSerializer(FavoriteRecipeSerializer):
    class Meta(FavoriteRecipeSerializer.Meta):
        model = ShoppingList

    def validate(self, data):
        request = self.context.get('request')
        recipe_id = data.get('recipe').id
        purchase_exists = ShoppingList.objects.filter(
            user=request.user,
            recipe__id=recipe_id
        ).exists()

        if request.method == 'GET' and purchase_exists:
            raise serializers.ValidationError(
                'The recipe is already on the shopping list.'
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return SubscriptionRecipeSerializer(
            instance.recipe,
            context=context).data
