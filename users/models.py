from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model


class Email(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user', default=None, null=True)
    address = models.CharField(default="", max_length=120)

    class Meta:
        ordering = ['address']

    def __str__(self):
        return self.address


class CustomUser(AbstractUser):
    email_addresses = models.ManyToManyField(Email)
