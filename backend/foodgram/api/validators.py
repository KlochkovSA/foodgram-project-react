from rest_framework.validators import ValidationError


def validate_cooking_time(value):
    if value < 1:
        raise ValidationError(
            "Убедитесь, что это значение больше либо равно 1.")
    return value


def validate_amount(value):
    if value < 1:
        raise ValidationError(
            "Убедитесь, что это значение больше либо равно 1.")
    return value
