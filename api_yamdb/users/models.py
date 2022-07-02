from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.db import models
from django.db.models import CheckConstraint, Q

from .validators import validate_username_not_me
from .managers import CustomUserManager


ROLES = (
    ('user', 'пользователь'),
    ('admin', 'администратор'),
    ('moderator', 'модератор')
)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(
        verbose_name='имя пользователя',
        max_length=150,
        unique=True,
        validators=[validate_username_not_me])
    email = models.EmailField(
        verbose_name='e-mail адрес',
        max_length=254,
        unique=True)
    role = models.CharField(
        verbose_name='роль пользователя',
        max_length=10,
        choices=ROLES,
        default='user')
    bio = models.TextField(
        verbose_name='биография',
        default='',
        blank=True)
    first_name = models.CharField(
        verbose_name='имя',
        max_length=150,
        default='',
        blank=True)
    last_name = models.CharField(
        verbose_name='фамилия',
        max_length=150,
        default='',
        blank=True)
    date_joined = models.DateTimeField(default=timezone.now)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ('email',)

    objects = CustomUserManager()

    def __str__(self):
        return f'{self.username} | {self.email}'

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_moderator(self):
        return self.role == 'moderator'

    class Meta:
        constraints = [
            CheckConstraint(
                check=~Q(username='me'),
                name='username_not_equal_me',
            ),
        ]
