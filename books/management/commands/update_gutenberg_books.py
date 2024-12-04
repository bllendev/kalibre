from django.core.management.base import BaseCommand
from django.db import transaction
from books.models import BookGutenberg
import boto3
import os
import ijson


"""
--bucket
kalibre-gutenberg-books

--key
gutenberg_book_records.json

docker compose exec web python manage.py update_gutenberg_books --bucket kalibre-gutenberg-books --key gutenberg_book_records.json
"""


class Command(BaseCommand):
    help = "Load books from a single JSON file stored in an S3 bucket and create BookGutenberg instances."

    def add_arguments(self, parser):
        parser.add_argument(
            "--bucket", type=str, help="The name of the S3 bucket", required=True
        )
        parser.add_argument(
            "--key",
            type=str,
            help="The key (file path) of the JSON file in the S3 bucket",
            required=True,
        )

    def handle(self, *args, **kwargs):
        bucket_name = kwargs["bucket"]
        file_key = kwargs["key"]

        s3 = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION"),
        )

        try:
            self.stdout.write(f"""
                Fetching file '{file_key}' from bucket '{bucket_name}'...
                """)
            response = s3.get_object(Bucket=bucket_name, Key=file_key)
            data_stream = response["Body"]

            books_to_create = []
            existing_titles = set(
                BookGutenberg.objects.filter(id__isnull=False).values_list(
                    "title", flat=True
                )
            )

            for book_data in ijson.items(data_stream, "item"):
                book_title = book_data.get("title")
                if not book_title or book_title in existing_titles:
                    continue

                book = BookGutenberg(
                    title=book_title,
                    json=book_data,
                    description=book_data.get("description", ""),
                    subjects=book_data.get("subjects", []),
                    bookshelves=book_data.get("bookshelves", []),
                )
                books_to_create.append(book)

                if len(books_to_create) >= 1000:  # Insert in batches
                    BookGutenberg.objects.bulk_create(books_to_create)
                    books_to_create = []

            # Insert remaining books
            if books_to_create:
                BookGutenberg.objects.bulk_create(books_to_create)

            self.stdout.write(self.style.SUCCESS(
                "All books processed successfully."))

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error accessing S3 or writing to DB: {e}")
            )


"""

{
    'id': 1,
    'format': 'Text',
    'title': 'The Declaration of Independence of the United States of America',
    'publishers': ['Project Gutenberg'],
    'description': 'This is the original PG edition.\r\nSee also our revised edition: #16780\r\nSee also #300',
    'downloads': '2249',
    'license': 'http://www.gutenberg.org/license',
    'subjects': [
        'United States -- History -- Revolution, 1775-1783 -- Sources',
        'United States. Declaration of Independence',
        'E201',
        'JK'
    ],
    'resources': [
        {
            'url': 'https://www.gutenberg.org/ebooks/1.html.images',
            'size': '54196',
            'modified': '2024-04-01T03:30:10.370954',
            'type': 'text/html'
        },
        {
            'url': 'https://www.gutenberg.org/files/1/1-h/1-h.htm',
            'size': '131865',
            'modified': '2021-01-28T05:38:53',
            'type': 'text/html'
        },
        {
            'url': 'https://www.gutenberg.org/files/1/1-h.zip',
            'size': '2189844',
            'modified': '2021-01-28T05:38:53',
            'type': 'text/html'
        },
        {
            'url': 'https://www.gutenberg.org/ebooks/1.epub3.images',
            'size': '2250551',
            'modified': '2024-04-01T03:30:16.313439',
            'type': 'application/epub+zip'
        },
        {
            'url': 'https://www.gutenberg.org/ebooks/1.epub.images',
            'size': '2247683',
            'modified': '2024-04-01T03:30:12.039936',
            'type': 'application/epub+zip'
        },
        {
            'url': 'https://www.gutenberg.org/ebooks/1.epub.noimages',
            'size': '81512',
            'modified': '2024-04-01T03:30:11.016947',
            'type': 'application/epub+zip'
        },
        {
            'url': 'https://www.gutenberg.org/ebooks/1.kf8.images',
            'size': '2430206',
            'modified': '2024-04-01T03:30:18.220474',
            'type': 'application/x-mobipocket-ebook'
        },
        {
            'url': 'https://www.gutenberg.org/ebooks/1.kindle.images',
            'size': '2422314',
            'modified': '2024-04-01T03:30:15.466464',
            'type': 'application/x-mobipocket-ebook'
        },
        {
            'url': 'https://www.gutenberg.org/ebooks/1.kindle.noimages',
            'size': '251909',
            'modified': '2022-09-01T03:30:13.576159',
            'type': 'application/x-mobipocket-ebook'
        },
        {
            'url': 'https://www.gutenberg.org/ebooks/1.txt.utf-8',
            'size': '118834',
            'modified': '2024-04-01T03:30:09.848942',
            'type': 'text/plain; charset=us-ascii'
        },
        {
            'url': 'https://www.gutenberg.org/files/1/1-0.txt',
            'size': '120943',
            'modified': '2021-01-01T05:10:10',
            'type': 'text/plain; charset=us-ascii'
        },
        {
            'url': 'https://www.gutenberg.org/files/1/1-0.zip',
            'size': '45741',
            'modified': '2021-01-01T05:10:10',
            'type': 'text/plain; charset=us-ascii'
        },
        {
            'url': 'https://www.gutenberg.org/ebooks/1.rdf',
            'size': '18690',
            'modified': '2024-04-01T03:30:18.374397',
            'type': 'application/rdf+xml'
        },
        {
            'url': 'https://www.gutenberg.org/cache/epub/1/pg1.cover.medium.jpg',
            'size': '23761',
            'modified': '2024-04-01T03:30:11.358948',
            'type': 'image/jpeg'
        },
        {
            'url': 'https://www.gutenberg.org/cache/epub/1/pg1.cover.small.jpg',
            'size': '4662',
            'modified': '2024-04-01T03:30:11.188990',
            'type': 'image/jpeg'
        },
        {
            'url': 'https://www.gutenberg.org/cache/epub/1/pg1-h.zip',
            'size': '2225859',
            'modified': '2024-04-01T03:30:10.412935',
            'type': 'application/octet-stream'
        }
    ],
    'languages': ['en'],
    'bookshelves': ['Politics', 'American Revolutionary War', 'United States Law'],
    'agents': {
        'Author': [{
            'name': 'Jefferson, Thomas',
            'alias': 'United States President (1801-1809)',
            'birth_date': '1743',
            'death_date': '1826',
            'webpage': 'https://en.wikipedia.org/wiki/Thomas_Jefferson'
        }]
    }
}
"""
