from django.db import models
import uuid

class Author(models.Model):
    """
    Represents an author with information such as name, birth and death dates, and a webpage link.
    """

    id = models.UUIDField(
        primary_key=True,
        db_index=True,
        default=uuid.uuid4,
        editable=False,
    )
    name = models.CharField(default="", null=False, blank=True, max_length=255, help_text="Full name of the author")
    alias = models.CharField(default="", max_length=255, blank=True, null=False, help_text="Alias or pen name, if applicable")
    birth_date = models.DateField(null=True, blank=True, help_text="Author's date of birth")
    death_date = models.DateField(null=True, blank=True, help_text="Author's date of death")
    webpage = models.URLField(max_length=200, blank=True, help_text="Link to the author's webpage or profile")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
        ]
        verbose_name_plural = "Authors"
