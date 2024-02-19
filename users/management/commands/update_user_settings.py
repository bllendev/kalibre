from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import UserSettings


class Command(BaseCommand):
    help = 'Create UserSettings for existing users'

    def handle(self, *args, **kwargs):
        users_without_settings = get_user_model().objects.filter(settings__isnull=True)
        for user in users_without_settings:
            UserSettings.objects.create(user=user)
            self.stdout.write(self.style.SUCCESS(f'Created settings for {user.username}'))
