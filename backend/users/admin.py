from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import FoodgramUser


@admin.register(FoodgramUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email',)
    search_fields = ('username', 'email',)
    list_filter = ('first_name', 'email',)
    fieldsets = []
    save_on_top = True
