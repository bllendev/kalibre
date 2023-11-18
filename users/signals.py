from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from users.models import UserSettings


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_settings(sender, instance, created, **kwargs):
    if created:
        UserSettings.objects.create(user=instance)
