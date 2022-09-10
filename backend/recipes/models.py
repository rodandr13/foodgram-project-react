from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from colorfield.fields import ColorField

User = get_user_model()
MAX_LEN_CHARFIELD = 200


class Ingredient(models.Model):
    name = models.CharField(
        'Название ингредиента',
        max_length=MAX_LEN_CHARFIELD,
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=MAX_LEN_CHARFIELD,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredients'
            ),
        )

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'


class Tag(models.Model):
    name = models.CharField(
        'Название тега',
        max_length=MAX_LEN_CHARFIELD,
    )
    color = ColorField(default='#999999',)
    slug = models.SlugField(
        'Слаг тега',
        max_length=MAX_LEN_CHARFIELD,
        unique=True,
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(
        'Название рецепта',
        max_length=MAX_LEN_CHARFIELD,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    text = models.TextField(
        'Описание'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=(
            MinValueValidator(
                1,
                'Не может быть меньше 1 минуты!'
            ),
            MaxValueValidator(
                600,
                'Не может быть больше 600 минут!'
            ),
        ),
    )
    image = models.ImageField(
        'Фото блюда',
        upload_to='media/',
        blank=True,
        null=True,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги',
        related_name='recipes',

    )
    favorite = models.ManyToManyField(
        User,
        verbose_name='В избранном',
        related_name='favorites',
        blank=True,
    )
    cart = models.ManyToManyField(
        User,
        verbose_name='Корзина',
        related_name='carts',
        blank=True,
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'author'),
                name='unique_recipe'
            ),
        )

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='Рецепты',
    )
    ingredients = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient',
        verbose_name='Ингредиенты',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=(
            MinValueValidator(
                1,
                'Необходимо добавить ингредиенты!'
            ),
            MaxValueValidator(
                1000,
                'Ингредиентов не может быть больше 1000'
            ),
        ),
    )

    class Meta:
        verbose_name = 'Ингредиент связанный'
        verbose_name_plural = 'Ингредиенты связанные'
        ordering = ['-id']
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredients',),
                name='unique_binding_ingredients',
            ),
        )

    def __str__(self):
        return f'{self.amount} {self.ingredients}'
