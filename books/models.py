import uuid
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.contrib.postgres.fields import JSONField
import urllib


class Book(models.Model):

    id = models.UUIDField(
        primary_key=True,
        db_index=True,
        default=uuid.uuid4,
        editable=False,
    )

    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    cover = models.ImageField(upload_to='covers/', blank=True)
    filetype = models.CharField(max_length=60, default="")
    isbn = models.CharField(max_length=200, default="")
    json_links = JSONField(null=True)

    def __str__(self):
        return f"{self.title} - {self.filetype} - {self.isbn}"

    def get_absolute_url(self):
        return reverse('book_detail', args=[str(self.id)])

    def _get_book_file_download_link(self, link):
        from bs4 import BeautifulSoup
        book_download_link = None
        with urllib.request.urlopen(link) as response:
            soup = BeautifulSoup(response.read(), "html.parser")
            book_download_link = soup.find_all('a')[0].get('href')
        return book_download_link

    def get_book_download_content(self, link):
        """
            - this takes scraps self.link, finding the
            specific download link to the book file.
        """
        import requests
        temp_book_file_dl = None
        try:
            user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
            values = {'name' : 'Michael Foord',
                    'location' : 'Northampton',
                    'language' : 'Python' }
            headers = { 'User-Agent' : user_agent }

            data = urllib.parse.urlencode(values)
            data = data.encode('ascii')
            book_download_link = self._get_book_file_download_link(link)
            # request = urllib.request.Request(book_download_link, data, headers)
            # temp_book_file_dl = urllib.request.urlopen(book_download_link, timeout=240)
            temp_book_file_dl = requests.get(book_download_link, timeout=240)
        except Exception as e:
            print(f"BAD LINK: {e}")
        return temp_book_file_dl

    @property
    def ssn(self):
        return f"book_{self.title}__type_{self.filetype}__isbn_{self.isbn}"

    class Meta:
        indexes = [
            models.Index(fields=['id'], name='id_index'),
        ]
        permissions = [
            ('special_status', 'Can read all books'),
        ]


class Review(models.Model):

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    review = models.CharField(max_length=255)
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    def __str__(self):
        return self.review