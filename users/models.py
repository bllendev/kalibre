from django.db import models
from django.conf import settings

from translate.constants import LANGUAGES


# ex. (("eng", "English"), ("es", "Español"), etc.)
LANUAGES_CONSTANTS = (
    (lang_code, lang_title)
    for lang_code, lang_title in LANGUAGES.items()
)


class Email(models.Model):
    TRANSLATE_CHOICES = LANUAGES_CONSTANTS
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user', default=None, null=True)
    address = models.CharField(default="", max_length=120)
    translate_file = models.CharField(max_length=20, choices=TRANSLATE_CHOICES, default="en", blank=True, null=False)

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

    @property
    def translate_book_bln(self):
        """
        returns True, if any emails of the user are active and have translate mode on.
        """
        translate_book_bln = False
        if self.email_addresses.all().exists():
            for email in self.email_addresses.all():
                if email.translate_file:
                    translate_book_bln = True
                    break
        return translate_book_bln
