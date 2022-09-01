from django.contrib import admin

from .models import Ingredient, IngredientInRecipe, Recipe, Tag

EMPTY_MESSAGE = '-пусто-'


class IngredientInRecipeInline(admin.TabularInline):
    model = IngredientInRecipe
    min_num = 1


@admin.register(IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    model = IngredientInRecipe


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)
    list_filter = ('name',)
    save_on_top = True
    empty_value_display = EMPTY_MESSAGE


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'is_favorited')
    search_fields = ('author', 'name', 'tags',)
    list_filter = ('author', 'name', 'tags')
    empty_value_display = EMPTY_MESSAGE
    inlines = (IngredientInRecipeInline,)

    def is_favorited(self, obj):
        return obj.favorite.count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug',)
    search_fields = ('name', 'color',)
    save_on_top = True
    empty_value_display = EMPTY_MESSAGE
