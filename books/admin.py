from django.contrib import admin
from books.models import Book, BookGutenberg


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    # inlines = [
    #     ReviewInline,
    # ]
    list_display = ("pk", "title", "description", "cover_url")
    search_fields = ("title", "isbns", "pk")


@admin.register(BookGutenberg)
class BookGutenbergAdmin(admin.ModelAdmin):
    # inlines = [
    #     ReviewInline,
    # ]
    list_display = ("pk", "title", "description")
    search_fields = ("title", "pk", "description", "subjects")
