from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Кастомная модель для пользователя."""

    ROLE_CHOICES = [
        ('user', 'Аутентифицированный пользователь'),
        ('admin', 'Администратор'),
    ]

    username = models.CharField('Никнейм', max_length=150, unique=True)
    email = models.EmailField('Почта', max_length=254, unique=True)
    password = models.TextField('Пароль', max_length=150)
    first_name = models.CharField('Имя', max_length=150)
    last_name = models.CharField('Фамилия', max_length=150)
    role = models.CharField(
        'Роль доступа',
        max_length=200,
        choices=ROLE_CHOICES,
        default='user',
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser

    @property
    def is_user(self):
        return self.role == 'user'

    def __str__(self):
        return self.username


class Subscribers(models.Model):
    """Модель подписчиков."""

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
        help_text='Подписчик на автора рецепта'
    )
    author = models.ForeignKey(
        CustomUser, null=True,
        on_delete=models.CASCADE,
        related_name='followed',
        verbose_name='Автор',
        help_text='Автор рецепта'
    )

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['author', 'user'],
            name='unique_object'
        )]

    def __str__(self):
        return f'{self.user} --> {self.author}'
