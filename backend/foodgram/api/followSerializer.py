from django.contrib.auth import get_user_model
from rest_framework import serializers

from users.serializers import UserGetSerializer
from .serializers import RecipeSerializer

User = get_user_model()


class FollowSerializer(UserGetSerializer):
    recipes = RecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()

    def get_recipes(self, obj):
        request = self.context.get('request')
        # default qty of objects in recipe field
        limit = 5
        if request and hasattr(request, 'recipes_limit'):
            limit = request.recipes_limit

        stores = obj.recipes.all()[:limit]
        return RecipeSerializer(stores, many=True, read_only=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed',
                  'recipes',
                  'recipes_count'
                  )
