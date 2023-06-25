from django.db import models, transaction

from ai.utils import get_openai_embeddings


class BookManager(models.Manager):
    def create_book(self, **kwargs):
        book = self.create(**kwargs)
        return book

    def create_and_embed_books(self, books_data, embedding_model="text-embedding-ada-002", max_tokens=8000):
        """
        Create books in bulk and generate embeddings for certain fields.
        """
        # Fields for which we need to generate embeddings
        fields_to_embed = ["title", "author", "filetype", "isbn"]

        with transaction.atomic():
            # bulk create books first
            books = [Book(**book_data) for book_data in books_data]
            books = Book.objects.bulk_create(books)

            for book in books:
                for field in fields_to_embed:
                    text = getattr(book, field)
                    embedding = get_openai_embeddings([text], embedding_model, max_tokens)

                    # Add this embedding to your vector database here.
                    # For example, if you use a method called 'add_embedding' in your vector database:
                    # vector_db.add_embedding(book.id, field, embedding[0])

        return books

    def create_and_embed_book(self, texts, embedding_model="text-embedding-ada-002", max_tokens=8000):
        """
        Create book and generate embeddings for certain fields.
        """
        # Create book first
        book = self.create_book(**texts)

        # Fields for which we need to generate embeddings
        fields_to_embed = ["title", "author", "filetype", "isbn"]

        for field in fields_to_embed:
            text = getattr(book, field)
            embedding = get_openai_embeddings([text], embedding_model, max_tokens)

            # Add this embedding to your vector database here.
            # For example, if you use a method called 'add_embedding' in your vector database:
            # vector_db.add_embedding(book.id, field, embedding[0])

        return book
