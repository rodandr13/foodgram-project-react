from string import hexdigits

from django.contrib.auth import get_user_model
from django.db.models import F
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from recipes.models import Ingredient, IngredientInRecipe, Recipe, Tag

User = get_user_model()


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = 'id', 'name', 'color', 'slug'

    def validate_color(self, color):
        color = str(color).strip('#')
        if not set(color).issubset(hexdigits):
            raise ValidationError(
                f'Цвет {color} должен быть шестнадцатиричным'
            )
        return f'#{color}'


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = 'id', 'name', 'measurement_unit'


class FavoriteCartRecipeSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = 'id', 'name', 'image', 'cooking_time'


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
        if user.is_anonymous or (user == obj):
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
        return obj.ingredients.values(
            'id', 'name', 'measurement_unit', amount=F('ingredient__amount')
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.carts.filter(id=obj.id).exists()

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.favorites.filter(id=obj.id).exists()

    def validate(self, data):
        tags = self.initial_data.get('tags')
        ingredients = self.initial_data.get('ingredients')
        ingredients_list = []
        ingredients_id = []
        if ingredients:
            for ingredient in ingredients:
                ingredient_id = ingredient.get('id')
                if ingredient_id in ingredients_id:
                    raise serializers.ValidationError(
                        'Ингредиенты должны быть уникальными'
                    )
                selected_ingredient = Ingredient.objects.filter(
                    id=ingredient_id
                )
                amount = ingredient.get('amount')
                ingredients_id.append(ingredient_id)
                ingredients_list.append(
                    {'ingredient': selected_ingredient, 'amount': amount}
                )
        data['tags'] = tags
        data['ingredients'] = ingredients_list
        data['author'] = self.context.get('request').user
        return data

    def create(self, validated_data):
        image = validated_data.pop('image')
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(image=image, **validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            IngredientInRecipe.objects.get_or_create(
                recipe=recipe,
                ingredients=ingredient['ingredient'][0],
                amount=ingredient['amount']
            )
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        if tags:
            instance.tags.clear()
            instance.tags.add(*tags)
        if ingredients:
            instance.ingredients.clear()
            for ingredient in ingredients:
                IngredientInRecipe.objects.get_or_create(
                    recipe=instance,
                    ingredients=ingredient['ingredient'][0],
                    amount=ingredient['amount']
                )
        instance.save()
        return instance
