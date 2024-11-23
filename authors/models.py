from django.db import models
import uuid


class Author(models.Model):
    id = models.UUIDField(
        primary_key=True,
        db_index=True,
        default=uuid.uuid4,
        editable=False,
    )
    key = models.CharField(
        default="",
        null=False,
        blank=True,
        max_length=255,
        help_text="The key id of the author.",
    )
    name = models.CharField(
        default="",
        null=False,
        blank=True,
        max_length=255,
        help_text="Full name of the author",
    )
    alternative_names = models.JSONField(default=list, blank=True, null=False)
    birth_date = models.DateField(
        null=True, blank=True, help_text="Author's date of birth"
    )
    death_date = models.DateField(
        null=True, blank=True, help_text="Author's date of death"
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
        ]
        verbose_name_plural = "Authors"
