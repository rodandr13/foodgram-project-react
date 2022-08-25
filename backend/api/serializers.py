from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer

from recipes.models import Ingredient, Tag, Recipe, IngredientInRecipe

User = get_user_model()


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = '__all__'


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = '__all__'


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class RecipeSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = '__all__'
