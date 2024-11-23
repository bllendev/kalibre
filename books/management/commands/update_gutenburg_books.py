from django.core.management.base import BaseCommand
from books.models import Book
import os
import json
import uuid


class Command(BaseCommand):
    help = "Load books from a directory of JSON files and create Book instances."

    def add_arguments(self, parser):
        parser.add_argument(
            "directory", type=str, help="The directory containing the JSON files"
        )

    def handle(self, *args, **kwargs):
        directory = kwargs["directory"]

        # Ensure the directory exists
        if not os.path.exists(directory):
            self.stdout.write(
                self.style.ERROR(f'Directory "{directory}" does not exist')
            )
            return

        # Iterate through all the JSON files in the directory
        for filename in os.listdir(directory):
            if filename.endswith(".json"):
                file_path = os.path.join(directory, filename)

                # Open and read the JSON file
                with open(file_path, "r") as json_file:
                    try:
                        data = json.load(json_file)
                        # Create Book instance
                        book, created = Book.objects.get_or_create(
                            id=uuid.uuid4(),
                            title=data.get("title", "Unknown Title"),
                            author=data["agents"]["Author"][0].get(
                                "name", "Unknown Author"
                            ),
                            json_links=data.get("resources", []),
                            isbns=data.get("id", ""),
                            cover_url=self.get_cover_image_url(
                                data.get("resources", [])
                            ),
                        )

                        if created:
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'Book "{book.title}" created successfully'
                                )
                            )
                        else:
                            self.stdout.write(
                                self.style.WARNING(
                                    f'Book "{book.title}" already exists'
                                )
                            )

                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'Error processing file "{
                                             filename}": {e}')
                        )

    def get_cover_image_url(self, resources):
        """Helper method to get the first available cover image URL"""
        for resource in resources:
            if resource.get("type") == "image/jpeg":
                return resource.get("url")
        return ""
