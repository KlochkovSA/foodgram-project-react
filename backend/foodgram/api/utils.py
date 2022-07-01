from rest_framework.decorators import (api_view, permission_classes,
                                       renderer_classes)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.models import ShoppingCart
from .renderer import TextRenderer



@api_view(['GET'])
@permission_classes([IsAuthenticated])
@renderer_classes([TextRenderer])
def download_shopping_cart(request):
    user = request.user
    shopping_cart = ShoppingCart.objects.filter(user=user).all()
    result_dict = {}
    for item in shopping_cart:
        for ingredient_amount in item.recipe.amounts.all():
            ingredient_id = ingredient_amount.ingredient_id
            # ingredient_id gives us string representation
            # of Ingredient model object
            key = f'{ingredient_id} ({ingredient_id.measurement_unit})'
            # Фарш (баранина и говядина) (г) — 600
            # if hasattr(result, key):
            if key in result_dict:
                result_dict[key] += ingredient_amount.amount
                continue
            result_dict[key] = ingredient_amount.amount
    result = ''.join([f'{k} - {v}\n' for k, v in result_dict.items()])
    return Response(result,
                    headers={'Content-Disposition':
                             'attachment; filename="file.txt"'},
                    status=status.HTTP_200_OK,
                    content_type='text/plain')
