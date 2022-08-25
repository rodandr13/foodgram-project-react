from django.contrib import admin

from .models import IngredientInRecipe, Tag, Recipe, Ingredient

EMPTY_MESSAGE = '-пусто-'


class IngredientInRecipeAdmin(admin.TabularInline):
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
    list_display = ('name', 'author',)
    search_fields = ('author', 'name', 'tags',)
    empty_value_display = EMPTY_MESSAGE
    inlines = (IngredientInRecipeAdmin,)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug',)
    search_fields = ('name', 'color',)
    save_on_top = True
    empty_value_display = EMPTY_MESSAGE
