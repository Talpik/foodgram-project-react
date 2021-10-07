from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import Ingredient, Tag, RecipeIngredient, User, Recipe
from .models import Subscription, ShoppingList, FavoriteRecipe


class UserSerializer(serializers.ModelSerializer):
    """
    Data serializer for the user model.
    Additionally adds the field whether
    the user is subscribed to other authors.

    """
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("email", "id", "username", "first_name",
                  "last_name", "is_subscribed")

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=request.user, author=obj.id
        ).exists()


class IngredientSerializer(serializers.ModelSerializer):
    """
    Data serializer for the Ingredient model.

    """
    class Meta:
        model = Ingredient
        fields = "__all__"


class TagSerializer(serializers.ModelSerializer):
    """
    Data serializer for the Tag model.

    """
    class Meta:
        model = Tag
        fields = "__all__"


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    """
     Data serializer for the RecipeIngredient model.
     Added field 'measurement_unit' through the ingredient model.

     """
    id = serializers.ReadOnlyField(source="ingredients.id")
    name = serializers.ReadOnlyField(source="ingredients.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredients.measurement_unit"
    )

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "amount", "measurement_unit")


class SubscriptionRecipeSerializer(serializers.ModelSerializer):
    """
    Data serializer for the Recipe model.

    """
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class RecipeSerializer(serializers.ModelSerializer):
    """
    Data serializer for the Recipe model.

    """
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientsSerializer(
        source="ingredients_amounts",
        many=True,
        read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ("id", "name", "author", "tags", "text",
                  "ingredients", "cooking_time", "image",
                  "is_favorited", "is_in_shopping_cart")

    def get_is_favorited(self, obj):
        """
        The method of processing the field 'is_favorited' -
        which allows you to determine whether this recipe
        is in the favorites of the requested user.
        For this, the FavoriteRecipe model
        is used in which this link is stored.

        """
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        return FavoriteRecipe.objects.filter(
            user=request.user, recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        """
        The method of processing the field 'is_in_shopping_cart' -
        which allows you to determine whether this recipe
        is in the shopping list of the requested user.
        For this, the ShoppingList model is used in which
        this link is stored.

        """
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        return ShoppingList.objects.filter(
            user=request.user, recipe=obj
        ).exists()

    def validate(self, data: dict) -> dict:
        """
        Validates the provided data for various errors.

        Args:
            data (dict): Dictionary with recipe's data.

        Returns:
            data (dict): Dictionary with recipe's data, in which was
            added ingredients id's.

        """
        ingredients = self.initial_data.get("ingredients")
        set_ingredients = set()
        if not ingredients:
            raise serializers.ValidationError(
                "Make sure that at least one ingredient has been added"
            )
        else:
            for ingredient in ingredients:
                if int(ingredient.get("amount")) <= 0:
                    raise serializers.ValidationError(
                        ("Make sure the value of the amount "
                         "ingredient is greater than 0")
                    )
                ingredient_id = ingredient.get("id")
                if ingredient_id in set_ingredients:
                    raise serializers.ValidationError(
                        "The ingredient in the recipe must not be repeated."
                    )
                set_ingredients.add(ingredient_id)
        data["ingredients"] = ingredients

        tags = self.initial_data.get("tags")
        if not tags:
            raise serializers.ValidationError(
                "Make sure that at least one tag has been added"
            )
        elif tags:
            if Tag.objects.filter(id__in=tags).count() < len(tags):
                raise serializers.ValidationError(
                    "Some tag not exist in database."
                )
        data["tags"] = tags

        cooking_time = self.initial_data.get("cooking_time")
        if cooking_time < 1:
            raise serializers.ValidationError(
                "Make sure that cooking time is grater then 0."
            )
        data["cooking_time"] = cooking_time

        return data

    def create(self, data: dict) -> Recipe:
        """
        Returns the generated model object Recipe
        based on the presented validated data.

        Args:
            data (dict): Validated data.

        Returns:
            recipe (Recipe): A new instance of recipe.

        """
        image = data.pop("image")
        ingredients = data.pop("ingredients")
        recipe = Recipe.objects.create(image=image, **data)
        tags = self.initial_data.get("tags")
        self.adding_tags_to_recipe(tags, recipe)
        self.save_ingredients_in_recipe(ingredients, recipe)

        return recipe

    def update(self, recipe: Recipe, data: dict) -> Recipe:
        """
        The method updates the recipe data -
        while first deleting all its tags and ingredients.

        Args:
            recipe (Recipe): A instance of recipe.
            data (dict): Updating data.

        Returns:
            recipe (Recipe): Updated instance of recipe.

        """
        recipe.tags.clear()
        tags = self.initial_data.get("tags")
        self.adding_tags_to_recipe(tags, recipe)

        RecipeIngredient.objects.filter(recipe=recipe).delete()
        ingredients = data.get("ingredients")
        self.save_ingredients_in_recipe(ingredients, recipe)

        if data.get("image") is not None:
            recipe.image = data.get("image")
        recipe.name = data.get("name")
        recipe.text = data.get("text")
        recipe.cooking_time = data.get("cooking_time")
        recipe.save()
        return recipe

    @staticmethod
    def adding_tags_to_recipe(tags, recipe):
        for tag_id in tags:
            recipe.tags.add(get_object_or_404(Tag, pk=tag_id))

    @staticmethod
    def save_ingredients_in_recipe(ingredients, recipe):
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get("id"),
                amount=ingredient.get("amount")
            )


class SubscriptionSerializer(serializers.ModelSerializer):
    """
    Data serializer for the Subscription model.

    """
    queryset = User.objects.all()
    user = serializers.PrimaryKeyRelatedField(queryset=queryset)
    author = serializers.PrimaryKeyRelatedField(queryset=queryset)

    class Meta:
        model = Subscription
        fields = ("user", "author")

    def validate(self, data: dict) -> dict:
        """
        Validates the provided data for various errors.

        Args:
            data (dict): Dictionary with Subscription's data.

        Returns:
            data (dict): Validated Subscription's data.

        """
        request = self.context.get("request")
        author_id = data.get("author").id
        subscription_exists = Subscription.objects.filter(
            user=request.user,
            author__id=author_id
        ).exists()

        if request.method == "GET":
            if request.user.id == author_id:
                raise serializers.ValidationError(
                    "You can't subscribe to yourself"
                )
            if subscription_exists:
                raise serializers.ValidationError(
                    "You are already following this user."
                )
        return data


class SubscriptionsSerializer(serializers.ModelSerializer):
    """
    Data serializer for the User model in case of subscriptions.

    """
    email = serializers.ReadOnlyField(source="author.email")
    id = serializers.ReadOnlyField(source="author.id")
    first_name = serializers.ReadOnlyField(source="author.first_name")
    last_name = serializers.ReadOnlyField(source="author.last_name")
    username = serializers.ReadOnlyField(source="author.username")
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "username",
                  "is_subscribed", "recipes", "recipes_count")

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=obj.user, author=obj.author
        ).exists()

    def get_recipes(self, obj):
        request = self.context.get("request")
        limit = request.GET.get("recipes_limit")
        queryset = Recipe.objects.filter(author=obj.author)
        if limit is not None:
            queryset = Recipe.objects.filter(
                author=obj.author
            )[:int(limit)]

        return SubscriptionRecipeSerializer(queryset, many=True).data

    @staticmethod
    def get_recipes_count(obj):
        """
        Handler for getting the number of recipes created by the user.

        """
        return Recipe.objects.filter(author=obj.author).count()


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """
    Data serializer for the FavoriteRecipe model.
    URL = 'recipes/favorite' or 'recipes/delete_favorite'

    """
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = FavoriteRecipe
        fields = ("user", "recipe")

    def validate(self, data):
        request = self.context.get("request")
        recipe_id = data.get("recipe").id
        favorite_exists = FavoriteRecipe.objects.filter(
            user=request.user,
            recipe__id=recipe_id
        ).exists()

        if request.method == "GET" and favorite_exists:
            raise serializers.ValidationError(
                "The recipe has already been added to favorites."
            )
        return data

    def to_representation(self, instance):
        request = self.context.get("request")
        context = {"request": request}
        return SubscriptionRecipeSerializer(
            instance.recipe,
            context=context).data


class ShoppingListSerializer(FavoriteRecipeSerializer):
    """
    Data serializer for the ShoppingList model.
    URL = 'recipes/shopping_cart' or 'recipes/delete_shopping_cart'

    """
    class Meta(FavoriteRecipeSerializer.Meta):
        model = ShoppingList

    def validate(self, data):
        request = self.context.get("request")
        recipe_id = data.get("recipe").id
        purchase_exists = ShoppingList.objects.filter(
            user=request.user,
            recipe__id=recipe_id
        ).exists()

        if request.method == "GET" and purchase_exists:
            raise serializers.ValidationError(
                "The recipe is already on the shopping list."
            )
        return data

    def to_representation(self, instance):
        request = self.context.get("request")
        context = {"request": request}
        return SubscriptionRecipeSerializer(
            instance.recipe,
            context=context).data
