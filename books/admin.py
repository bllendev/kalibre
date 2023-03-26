from django.contrib import admin
from books.models import Book, Review


class ReviewInline(admin.TabularInline):
    model = Review


class BookAdmin(admin.ModelAdmin):
    inlines = [
        ReviewInline,
    ]
    list_display = ("pk", "title", "author", "price", "isbn")
    search_fields = ("title", "author", "isbn", "pk")


admin.site.register(Book, BookAdmin)
