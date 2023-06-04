from rest_framework import serializers
from books.models import Book


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = [
            'id',
            'title',
            '_title_lemmatized',
            'author',
            'price',
            'cover',
            'filetype',
            'isbn',
            'json_links'
        ]
