from django.db import models

from users.models import User
from .validators import validate_score, validate_year


class Category(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        verbose_name = 'категории'

    def __str__(self) -> str:
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)


class Title(models.Model):
    name = models.TextField()
    year = models.IntegerField(validators=[validate_year],)
    description = models.TextField(
        null=True,
        blank=True
    )
    genre = models.ManyToManyField(Genre)
    category = models.ForeignKey(
        Category,
        related_name='titles',
        null=True,
        blank=True,
        on_delete=models.SET_NULL)


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    text = models.TextField(
        'Отзыв'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews')
    score = models.IntegerField(
        validators=[validate_score])
    pub_date = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ['-pub_date']
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='title_author_unique')
        ]


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ['-pub_date']
