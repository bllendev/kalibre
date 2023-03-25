from django.db import models
from django.conf import settings


class Email(models.Model):
    TRANSLATE_EN_ES = 'English to Spanish'
    TRANSLATE_CHOICES = (
        (TRANSLATE_EN_ES, 'en-es'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user', default=None, null=True)
    address = models.CharField(default="", max_length=120)
    translate_file = models.CharField(max_length=20, choices=TRANSLATE_CHOICES, default="", blank=True, null=False)

    class Meta:
        ordering = ['address']

    def __str__(self):
        return self.address


from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    email_addresses = models.ManyToManyField(Email)

    @property
    def emails_exist(self):
        return self.email_addresses.all().exists()

    @property
    def email_addresses_str(self):
        email_list = list([email.address for email in self.email_addresses.all().order_by('-address')])
        email_str = "\n".join(email_list)
        return email_str
