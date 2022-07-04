from django.core.exceptions import ValidationError
import datetime as dt


def validate_year(year):
    now_year = dt.date.today()
    if year > now_year.year:
        raise ValueError(f'Некорректный год {year}')


def validate_score(value):
    if value < 1 or value > 10:
        raise ValidationError('Оценка должна быть от 1 до 10!')
