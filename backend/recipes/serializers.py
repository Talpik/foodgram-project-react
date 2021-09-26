from recipes.models import Ingredient

from rest_framework import serializers


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'
