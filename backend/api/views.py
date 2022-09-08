from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from djoser.views import UserViewSet

from recipes.models import Ingredient, IngredientInRecipe, Recipe, Tag
from .pagination import LimitPageNumberPagination
from .permissions import AdminOrReadOnly, AuthorStaffOrReadOnly
from .serializers import (
    FavoriteCartRecipeSerializer,
    IngredientSerializer,
    RecipeSerializer,
    SubscribeSerializer,
    TagSerializer,
    UserSerializer
)


User = get_user_model()


class PostDeleteView:

    def __post_del_obj__(self, user_id, action):
        user = self.request.user
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        actions = {
            'subscribe': user.subscribe,
            'cart': user.carts,
            'favorite': user.favorites,
        }
        current_user = actions[action]
        queryset = get_object_or_404(self.queryset, id=user_id)
        serializer = self.add_serializer(
            queryset, context={'request': self.request}
        )
        recipe_exist = current_user.filter(id=user_id).exists()
        if self.request.method == 'POST' and not recipe_exist:
            current_user.add(queryset)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if self.request.method == 'DELETE' and recipe_exist:
            current_user.remove(queryset)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly,)
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AdminOrReadOnly,)
    pagination_class = None


class UserViewSet(UserViewSet, PostDeleteView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    add_serializer = SubscribeSerializer
    pagination_class = LimitPageNumberPagination

    @action(methods=('GET',), detail=False)
    def subscriptions(self, request):
        user = self.request.user
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        authors = user.subscribe.all()
        pages = self.paginate_queryset(authors)
        serializer = SubscribeSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(methods=('POST', 'DELETE'), detail=True)
    def subscribe(self, request, id):
        action = 'subscribe'
        return self.__post_del_obj__(id, action)


class RecipeViewSet(ModelViewSet, PostDeleteView):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (AuthorStaffOrReadOnly,)
    add_serializer = FavoriteCartRecipeSerializer
    pagination_class = LimitPageNumberPagination

    @staticmethod
    def __ingredientInRecipeFilter__(user):
        ingredients = IngredientInRecipe.objects.filter(
            recipe__in=(user.carts.values('id'))
        ).values(
            'ingredients__name',
            'ingredients__measurement_unit'
        ).annotate(amount=Sum('amount'))
        return ingredients

    def get_queryset(self):
        queryset = self.queryset
        tags = self.request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()
        user = self.request.user
        if user.is_anonymous:
            return queryset
        author = self.request.query_params.get('author')
        if author:
            queryset = queryset.filter(author=author)
        is_in_shopping = self.request.query_params.get('is_in_shopping_cart')
        if is_in_shopping == '1':
            queryset = queryset.filter(cart=user.id)
        elif is_in_shopping == '0':
            queryset = queryset.exclude(cart=user.id)
        is_favorited = self.request.query_params.get('is_favorited')
        if is_favorited == '1':
            queryset = queryset.filter(favorite=user.id)
        elif is_favorited == '0':
            queryset = queryset.exclude(favorite=user.id)
        return queryset

    @action(detail=True, methods=('POST', 'DELETE'))
    def favorite(self, request, pk=None):
        action = 'favorite'
        return self.__post_del_obj__(pk, action)

    @action(detail=True, methods=('POST', 'DELETE'))
    def shopping_cart(self, request, pk):
        action = 'cart'
        return self.__post_del_obj__(pk, action)

    @action(methods=('GET',), detail=False)
    def download_shopping_cart(self, request):
        user = request.user
        if not user.carts.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        ingredients = self.__ingredientInRecipeFilter__(user)
        shop_list = 'Список покупок: \n'
        for ingredient in ingredients:
            shop_list += (
                f"{ingredient['ingredients__name']} — "
                f"{ingredient['amount']} "
                f"({ingredient['ingredients__measurement_unit']})\n"
            )
        return HttpResponse(shop_list, content_type='text/plain')
