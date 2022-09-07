from django.contrib.auth.models import AbstractUser
from django.db import models

MAX_LEN_CHARFIELD = 200


class FoodgramUser(AbstractUser):
    email = models.EmailField(
        'Email',
        max_length=MAX_LEN_CHARFIELD,
        unique=True,
    )
    username = models.CharField(
        'Юзернейм',
        max_length=MAX_LEN_CHARFIELD,
        unique=True,
    )
    first_name = models.CharField(
        'Имя',
        max_length=MAX_LEN_CHARFIELD,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=MAX_LEN_CHARFIELD,
    )
    subscribe = models.ManyToManyField(
        to='self',
        verbose_name='Подписки',
        related_name='subscribers',
        symmetrical=False,
        blank=True,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('-id',)

    def __str__(self):
        return f'{self.username}'
