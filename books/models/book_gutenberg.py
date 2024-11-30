# django
from django.db import models

# tools
import uuid

# local

# logs
import logging

logger = logging.getLogger(__name__)


class BookGutenberg(models.Model):
    """
    Represents a single book, capturing key data as
    returned from Gutenberg results.
    """

    URL_TYPE_MAP = {
        "pdf.pdf": "PDF",
        "epub.noimage": "EPUB (No images, Older E-readers)",
        "kindle.images": "Kindle",
        "kindle": "Older Kindles",
        "txt.utf-8": "Plain Text UTF-8",
        "epub.zip": "Download HTML (.zip)",
    }

    id = models.UUIDField(
        primary_key=True,
        db_index=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the book instance.",
    )
    json = models.JSONField(
        default=dict, blank=True, help_text="The original captured data."
    )  # self.json['resources']  -> list of dicts of links
    title = models.CharField(
        default="", blank=True, help_text="The title of the book", null=False
    )
    description = models.TextField(
        blank=True, null=True, help_text="A description of the book if provided."
    )

    subjects = models.JSONField(
        default=list, blank=True, help_text="List of subjects covered by the book."
    )
    bookshelves = models.JSONField(
        default=list, blank=True, help_text="List of bookshelves covered by the book."
    )

    def get_links(self):
        """
        returns: dict of links
        ex... {file_type: url}
        """
        links = dict()
        for link_dict in self.json["resources"]:
            url = link_dict["url"]
            for url_ending, file_type in self.URL_TYPE_MAP.items():
                if url_ending in url:
                    links[file_type] = url
                    break

        print(f"links: {links}")
        return links
