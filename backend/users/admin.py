from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email',)
    search_fields = ('username', 'email',)
    list_filter = ('first_name', 'email',)
    fieldsets = []
    save_on_top = True
