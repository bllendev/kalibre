from django.contrib.auth.models import AbstractUser
from django.db import models


class Email(models.Model):
    address = models.CharField(default="", max_length=120)

    class Meta:
        ordering = ['address']

    def __str__(self):
        return self.address


class CustomUser(AbstractUser):
    email_address = models.ManyToManyField(Email)
