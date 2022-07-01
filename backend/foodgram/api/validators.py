from rest_framework.validators import UniqueValidator, ValidationError

from recipes.models import Tag


def validate_cooking_time(value):
    if value < 1:
        raise ValidationError(
            "Убедитесь, что это значение больше либо равно 1.")
    return value


def unique_tag():
    return UniqueValidator(queryset=Tag.objects.all())


def validate_amount(value):
    if value < 1:
        raise ValidationError(
            "Убедитесь, что это значение больше либо равно 1.")
    return value
