import os
import csv

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.conf import settings

from reviews.models import (
    Category,
    Genre,
    GenreTitle,
    Title,
    Comment,
    Review,
)


PATH = os.path.join(settings.BASE_DIR, 'static', 'data')
User = get_user_model()

FILE_TO_TABLE = {
    'users.csv': User,
    'category.csv': Category,
    'genre.csv': Genre,
    'titles.csv': Title,
    'genre_title.csv': GenreTitle,
    'review.csv': Review,
    'comments.csv': Comment,
}


class Command(BaseCommand):
    help = 'Fills the database'

    def handle(self, *args, **kwargs):
        for file_name, model in FILE_TO_TABLE.items():
            model.objects.all().delete()
            if file_name not in os.listdir(PATH):
                continue
            with open(
                    os.path.join(PATH, file_name),
                    'r',
                    encoding='utf-8') as file:
                lines = csv.reader(file, delimiter=',', quotechar='"')
                header = next(lines)
                for line in lines:
                    print(line)
                    data = {key: value for key, value in zip(header, line)}
                    if model is Title:
                        data['category'] = Category.objects.get(
                            id=int(data['category']))
                    elif model is Comment or model is Review:
                        data['author'] = User.objects.get(
                            id=int(data['author']))
                    model.objects.create(**data)
