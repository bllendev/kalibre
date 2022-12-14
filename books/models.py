import uuid
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse


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
    link = models.CharField(max_length=562, default="")       # see get_book_download_link
    filetype = models.CharField(max_length=60, default="")
    isbn = models.CharField(max_length=200, default="", unique=True)

    def __str__(self):
        return f"{self.title} - {self.filetype} - {self.link}"

    def get_absolute_url(self):
        return reverse('book_detail', args=[str(self.id)])

    def get_book_download_link(self, link):
        """
            - this takes scraps self.link, finding the
            specific download link to the book file.
        """
        from bs4 import BeautifulSoup
        import requests

        response = requests.get(link)
        soup = BeautifulSoup(response.content, "html.parser")
        book_download_link = soup.find_all('a')[0].get('href')
        return book_download_link

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