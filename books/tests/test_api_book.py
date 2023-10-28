import os
from django.test import TestCase
from unittest.mock import Mock

# local
from books.api.api_book import APIBook


class TestAPIBook(TestCase):

    def test_libgen_data(self):
        book = APIBook(ID="12345", Author="John Doe", Title="Sample Book")
        
        expected_values = {
            "isbn": "12345",
            "author": "John Doe",
            "title": "Sample Book",
        }
        
        for key, value in expected_values.items():
            self.assertEqual(book[key], value)

    def test_openlibrary_data(self):
        book = APIBook(key="works/OL20157354W", author_name=["John Doe"], title="Sample Book", cover_i=8802446)

        expected_values = {  # NOTE: should correspond Book db fields
            "isbn": "works/OL20157354W",
            "author": "John Doe",
            "title": "Sample Book",
            "cover_url": "https://covers.openlibrary.org/b/id/8802446-L.jpg",  # OL20157354W
        }
        
        for key, value in expected_values.items():
            self.assertEqual(book[key], value)

    def test_set_api_books(self):
        """calling set() should unique-ify books"""
        # openlibrary
        book1 = APIBook(ID="12345", Author="John Doe", Title="Sample Book", Extension="epub")
        book2 = APIBook(ID="12345", Author="John Doe", Title="Sample Book", Extension="epub")
        book_set = set([book1, book2])
        self.assertTrue(len(book_set) == 1)
    
    def test_iter(self):
        book = APIBook(ID="12345", Author="John Doe", Title="Sample Book", Extension="pdf")
        for key, value in book:
            self.assertEqual(value, book[key])

    def test_getattr(self):
        book = APIBook(ID="12345", Author="John Doe", Title="Sample Book", Extension="pdf")
        self.assertEqual(book.title, "Sample Book")
        with self.assertRaises(AttributeError):
            _ = book.nonexistent_key

    def test_setattr(self):
        book = APIBook(**{"title": "test_book"})
        self.assertEqual(book.title, "test_book")

    def test_eq(self):
        book1 = APIBook(ID="12345", Author="John Doe", Title="Sample Book", Extension="pdf")
        book2 = APIBook(ID="12345", Author="John Doe", Title="Sample Book", Extension="pdf")
        self.assertEqual(book1, book2)
        book3 = APIBook(ID="67890", Author="John Doe", Title="Another Book", Extension="pdf")
        self.assertNotEqual(book1, book3)
