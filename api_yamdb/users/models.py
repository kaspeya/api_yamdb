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
    first_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(
        verbose_name='email',
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
        max_length=20,
        choices=ROLES,
        default=USER
    )
    confirmation_code = models.CharField(max_length=255)

    @property
    def is_admin(self):
        return (
            self.role == ADMIN or self.is_staff
            or self.is_superuser
        )

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    def __str__(self):
        return self.username
