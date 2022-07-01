from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import serializers

from users.serializers import UserGetSerializer
from .serializers import RecipeSerializer

User = get_user_model()


class FollowSerializer(UserGetSerializer):
    recipes = RecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.IntegerField(
        source='recipes.count',
        read_only=True
    )

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = settings.FOLLOW_SERIALIZER_RECIPES_LIMIT
        if request and hasattr(request, 'recipes_limit'):
            limit = request.recipes_limit
        recipes = obj.recipes.all()[:limit]
        return RecipeSerializer(recipes, many=True, read_only=True).data

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed',
                  'recipes',
                  'recipes_count'
                  )
