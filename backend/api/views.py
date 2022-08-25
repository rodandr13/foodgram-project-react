from django.contrib.auth import get_user_model
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipes.models import Ingredient, Tag, Recipe, IngredientInRecipe
from .serializers import TagSerializer, IngredientSerializer, UserSerializer, RecipeSerializer


User = get_user_model()


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class UserViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = UserSerializer


class RecipeViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = RecipeSerializer