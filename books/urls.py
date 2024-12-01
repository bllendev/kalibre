from django.urls import path
from books import views


urlpatterns = [
    # core views
    # path('', include(router.urls)),
    path("<uuid:pk>", views.BookDetailView.as_view(), name="book-detail"),
    path(
        "search-results/",
        views.SearchResultsView.as_view(),
        name="search-results",
    ),
    path(
        "search-results/<str:query>/",
        views.SearchResultsView.as_view(),
        name="search-results",
    ),
    path(
        "book-search/",
        views.BookSearchView.as_view(),
        name="book-search",
    ),
    path(
        "book-search/<str:query>/",
        views.BookSearchView.as_view(),
        name="book-search",
    ),
    path(
        "book-search-openlibrary/",
        views.BookSearchOpenlibraryView.as_view(),
        name="book-search-openlibrary",
    ),
    path(
        "book-save-vector/<uuid:pk>/",
        views.BookSaveVectorView.as_view(),
        name="book-save-vector",
    ),
    # book
    path("get-cover/<uuid:pk>/", views.GetCoverView.as_view(), name="get-cover"),
    path(
        "send-book-gutenberg/<uuid:pk>/",
        views.SendBookGutenbergView.as_view(),
        name="send-book-gutenberg",
    ),
    path(
        "get-gutenberg-links/<uuid:pk>/",
        views.GetGutenbergLinksView.as_view(),
        name="get-gutenberg-links",
    ),
]
