from django.db import models
from django.conf import settings

from collections import defaultdict

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

    @staticmethod
    def get_email_dict(emails):
        grouped_emails = defaultdict(list)

        # build grouped emails (by language)
        for email_obj in emails:
            grouped_emails[email_obj.translate_file].append(email_obj.address)

        # convert defaultdict to regular dict for the final result
        return dict(grouped_emails)

    class Meta:
        ordering = ['address']

    def __str__(self):
        return self.address


class UserSettings(models.Model):
    # notifications
    notifications = models.JSONField(default={
        "notify_ebook_convert": True,
    })

    # settings
    setting_ebook_convert = models.CharField(default="", blank=True)

    def get_notification(self, notification_str):
        return self.notifications.get(notification_str, None)

    def set_notification(self, notification_str, set_bool):
        current_value = self.notifications.get(notification_str)
    
        # Check if the notification setting exists and if the new value is different
        if current_value is not None and current_value != set_bool:
            self.notifications[notification_str] = set_bool
            self.save()

    class Meta:
        verbose_name = "User Setting"
        verbose_name_plural = "User Settings"


from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """search history stoored and presented locally
    """
    email_addresses = models.ManyToManyField("users.Email")
    my_books = models.ManyToManyField("books.Book")
    settings = models.OneToOneField("users.UserSettings", on_delete=models.CASCADE, related_name='user', null=True)

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
                if email.translate_file != "en":
                    translate_book_bln = True
                    break
        return translate_book_bln
