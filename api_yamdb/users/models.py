from django.contrib.auth.models import AbstractUser
from django.db import models


ADMIN = 'admin'
MODERATOR = 'moderator'
USER = 'user'

ROLES = (
    (ADMIN, ADMIN),
    (MODERATOR, MODERATOR),
    (USER, USER),
)


class User(AbstractUser):
    username = models.CharField(
        verbose_name='имя пользователя',
        max_length=150,
        unique=True,
    )
    email = models.EmailField(
        verbose_name='e-mail адрес',
        unique=True,
        max_length=254
    )
    bio = models.TextField(
        verbose_name='биография',
        blank=True,
        null=True,
    )
    role = models.CharField(
        verbose_name='роль пользователя',
        choices=ROLES,
        max_length=max(len(role[1]) for role in ROLES),
        default=USER
    )
    first_name = models.CharField(
        verbose_name='имя',
        max_length=150,
        blank=True)
    last_name = models.CharField(
        verbose_name='фамилия',
        max_length=150,
        blank=True
    )
    confirmation_code = models.CharField(max_length=255)

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('username', 'email',),
                name='unique_user'
            ),
        )

    @property
    def is_admin(self):
        return (self.role == ADMIN or self.is_staff
                or self.is_superuser)

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    def __str__(self):
        return self.username
