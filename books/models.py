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
    link = models.CharField(max_length=280, default="")
    filetype = models.CharField(max_length=60, default="")

    def __str__(self):
        return f"{self.title} - {self.filetype} - {self.link}"

    def get_absolute_url(self):
        return reverse('book_detail', args=[str(self.id)])

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