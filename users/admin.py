from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from users.models import Email, UserSettings


CustomUser = get_user_model()


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ('email', 'username', 'email_addresses_list', 'books_count', 'translate_book_status')
    list_filter = ('email_addresses',)
    search_fields = ('email', 'username',)

    def email_addresses_list(self, obj):
        return format_html("<br>".join([email.address for email in obj.email_addresses.all()]))
    email_addresses_list.short_description = 'Email Addresses'

    def books_count(self, obj):
        return obj.my_books.count()
    books_count.short_description = 'Number of Books'

    def translate_book_status(self, obj):
        return 'Yes' if obj.translate_book_bln else 'No'
    translate_book_status.short_description = 'Translate Book Enabled'

admin.site.register(CustomUser, CustomUserAdmin)


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ("address", "translate_file", "user")


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ('id', 'notification_settings', 'setting_ebook_convert')
    search_fields = ('id',)

    def notification_settings(self, obj):
        return format_html(
            '<pre>{}</pre>', 
            obj.notifications
        )

    def has_add_permission(self, request):
        # Disable the add functionality
        return False
