from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from users.models import Email


CustomUser = get_user_model()


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = [
        'email',
        'username',
    ]


admin.site.register(CustomUser, CustomUserAdmin)


class EmailAdmin(admin.ModelAdmin):
    list_display = ("address", "translate_file", "user")


admin.site.register(Email, EmailAdmin)
