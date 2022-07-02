from django.core.exceptions import ValidationError


def validate_score(value):
    if value < 1 or value > 10:
        raise ValidationError('Score must be between 1 and 10')
