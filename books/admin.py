from django.contrib import admin
from books.models import Book, Review


class ReviewInline(admin.TabularInline):
    model = Review


class BookAdmin(admin.ModelAdmin):
    inlines = [
        ReviewInline,
    ]
    list_display = ("title", "author", "price",)


admin.site.register(Book, BookAdmin)
