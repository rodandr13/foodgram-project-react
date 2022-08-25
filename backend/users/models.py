from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    email = models.EmailField(
        'Email',
        max_length=200,
        unique=True,
    )
    username = models.CharField(
        'Юзернейм',
        max_length=200,
        unique=True,
    )
    first_name = models.CharField(
        'Имя',
        max_length=200,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=200,
    )
    subscribe = models.ManyToManyField(
        to='self',
        verbose_name='Подписки',
        related_name='subscribers',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('-id',)

    def __str__(self):
        return f'{self.username}'
