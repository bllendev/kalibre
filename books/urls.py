from django.urls import path, include
from rest_framework.routers import DefaultRouter

from books import views
from books import ajax


urlpatterns = [
    # core views
    # path('', include(router.urls)),
    path('<uuid:pk>', views.BookDetailView.as_view(), name='book_detail'),
    path('search-results/', views.search_results, name='search_results'),
    path('book-search/<str:original_query>/', views.BookSearch.as_view(), name='book-search'),
    path('book-search-refresh/<str:original_query>/', views.BookSearchRefresh.as_view(), name='book-search-refresh'),

    # book
    path('get-cover/<uuid:pk>/', views.GetCover.as_view(), name='get-cover'),

    # ajax
    path("send-book-ajax/<uuid:pk>/", ajax.send_book_ajax, name="send_book_ajax"),
]
