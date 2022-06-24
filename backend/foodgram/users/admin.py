from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Follow

User = get_user_model()
admin.site.unregister(User)


class UserAdmin(BaseUserAdmin):
    search_fields = ('email', 'username')


admin.site.register(User, UserAdmin)


@admin.register(Follow)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = ('user', 'author', 'created')
