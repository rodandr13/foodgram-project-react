from django.contrib.auth import get_user_model
from django.db.models import F
from django.shortcuts import get_object_or_404
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from drf_extra_fields.fields import Base64ImageField

from recipes.models import Ingredient, Tag, Recipe, IngredientInRecipe

User = get_user_model()


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ('__all__',)


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = ('__all__',)


class FavoriteCartRecipeSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = 'id', 'name', 'image', 'cooking_time'
        read_only_fields = ('__all__',)


class UserSerializer(ModelSerializer):
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'password',
        )
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = ('is_subscribed',)

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated or (user == obj):
            return False
        return user.subscribe.filter(id=obj.id).exists()


class SubscribeSerializer(UserSerializer):
    recipes = FavoriteCartRecipeSerializer(many=True, read_only=True)
    recipes_count = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        read_only_fields = '__all__',

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class RecipeSerializer(ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    is_favorited = SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_in_shopping_cart',
            'is_favorited',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_ingredients(self, obj):
        ingredients = obj.ingredients.values(
            'id', 'name', 'measurement_unit', amount=F('ingredient__amount')
        )
        return ingredients

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return user.carts.filter(id=obj.id).exists()

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return user.favorites.filter(id=obj.id).exists()

    def validate(self, data):
        tags = self.initial_data.get('tags')
        ingredients = self.initial_data.get('ingredients')
        valid_ingredients = []
        for ing in ingredients:
            ing_id = ing.get('id')
            ingredient = Ingredient.objects.filter(id=ing_id)
            amount = ing.get('amount')
            valid_ingredients.append(
                {'ingredient': ingredient, 'amount': amount}
            )
        data['tags'] = tags
        data['ingredients'] = valid_ingredients
        data['author'] = self.context.get('request').user
        return data

    def create(self, validated_data):
        image = validated_data.pop('image')
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(image=image, **validated_data)
        recipe.tags.set(tags)
        counter = 0
        for ingredient in ingredients:
            IngredientInRecipe.objects.get_or_create(
                recipe=recipe,
                ingredients=ingredient['ingredient'][counter],
                amount=ingredient['amount']
            )
            counter += 1
        return recipe

    def update(self, recipe, validated_data):
        tags = validated_data.get('tags')
        ingredients = validated_data.get('ingredients')
        recipe.image = validated_data.get('image', recipe.image)
        recipe.name = validated_data.get('name', recipe.name)
        recipe.text = validated_data.get('text', recipe.text)
        recipe.cooking_time = validated_data.get(
            'cooking_time', recipe.cooking_time
        )
        if tags:
            recipe.tags.clear()
            recipe.tags.set(tags)
        counter = 0
        for ingredient in ingredients:
            IngredientInRecipe.objects.get_or_create(
                recipe=recipe,
                ingredients=ingredient['ingredient'][counter],
                amount=ingredient['amount']
            )
            counter += 1
        recipe.save()
        return recipe
