import csv
from django.db.models import Sum
from django.db.models import F
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework import status
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from recipes.models import Ingredient, Tag, Recipe, IngredientInRecipe
from .serializers import TagSerializer, IngredientSerializer, UserSerializer, RecipeSerializer, FavoriteCartRecipeSerializer, SubscribeSerializer
from .permissions import AdminOrReadOnly, AuthorStaffOrReadOnly
from .pagination import LimitPageNumberPagination
from djoser.views import UserViewSet

User = get_user_model()


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly,)


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AdminOrReadOnly,)


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    add_serializer = SubscribeSerializer
    pagination_class = LimitPageNumberPagination

    @action(methods=('get',), detail=False)
    def subscriptions(self, request):
        print('++++++++++++')
        print('test2')
        user = self.request.user
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        authors = user.subscribe.all()
        pages = self.paginate_queryset(authors)
        serializer = SubscribeSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(methods=('get','delete'), detail=True)
    def subscribe(self, request, id):
        print('test')
        user = request.user
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        user_subscribe = user.subscribe
        recipe = get_object_or_404(self.queryset, id=id)
        print(recipe)
        serializer = self.add_serializer(
            recipe, context={'request': self.request}
        )
        recipe_exist = user_subscribe.filter(id=id).exists()
        if self.request.method == 'GET' and not recipe_exist:
            user_subscribe.add(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == 'DELETE' and recipe_exist:
            user_subscribe.remove(recipe)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    #permission_classes = (AuthorStaffOrReadOnly,)
    add_serializer = FavoriteCartRecipeSerializer
    pagination_class = LimitPageNumberPagination

    def get_queryset(self):
        queryset = self.queryset
        tags = self.request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(
                tags__slug__in=tags).distinct()
        author = self.request.query_params.get('author')
        if author:
            queryset = queryset.filter(author=author)
        user = self.request.user
        if user.is_anonymous:
            return queryset
        is_in_shopping = self.request.query_params.get('is_in_shopping_cart')
        if is_in_shopping:
            queryset = queryset.filter(cart=user.id)
        elif is_in_shopping:
            queryset = queryset.exclude(cart=user.id)
        is_favorited = self.request.query_params.get('is_favorited')
        if is_favorited:
            queryset = queryset.filter(favorite=user.id)
        if is_favorited:
            queryset = queryset.exclude(favorite=user.id)
        return queryset

    @action(detail=True, methods=["get", "delete"], )
    def favorite(self, request, pk=None):
        user = request.user
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        user_favorites = user.favorites
        recipe = get_object_or_404(self.queryset, id=pk)
        serializer = self.add_serializer(
            recipe, context={'request': self.request}
        )
        recipe_exist = user_favorites.filter(id=pk).exists()
        if self.request.method == 'GET' and not recipe_exist:
            user_favorites.add(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == 'DELETE' and recipe_exist:
            user_favorites.remove(recipe)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get', 'delete'],)
    def shopping_cart(self, request, pk):
        user = request.user
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        user_cart = user.carts
        recipe = get_object_or_404(self.queryset, id=pk)
        serializer = self.add_serializer(
            recipe, context={'request': self.request}
        )
        recipe_exist = user_cart.filter(id=pk).exists()
        if self.request.method == 'GET' and not recipe_exist:
            user_cart.add(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == 'DELETE' and recipe_exist:
            user_cart.remove(recipe)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=('get',), detail=False)
    def download_shopping_cart(self, request):
        user = request.user
        if not user.carts.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        ingredients = IngredientInRecipe.objects.filter(
            recipe__in=(user.carts.values('id'))
        ).values(
            ingredient=F('ingredients__name'),
            measure=F('ingredients__measurement_unit')
        ).annotate(amount=Sum('amount'))
        shopping_list = []
        for ing in ingredients:
            shopping_list.append([ing["ingredient"], ing["amount"], ing["measure"]])
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = ('attachment;'
                                           'filename="Shoppingcart.csv"')
        response.write(u'\ufeff'.encode('utf8'))
        writer = csv.writer(response)
        for item in shopping_list:
            writer.writerow(item)
        return response
