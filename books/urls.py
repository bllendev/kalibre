from django.urls import path
from books import views


urlpatterns = [
    path('', views.BookListView.as_view(), name='book_list'),
    path('<uuid:pk>', views.BookDetailView.as_view(), name='book_detail'),
    path('search_results/', views.search_results, name='search_results'),

    # email
    path("my_emails/", views.my_emails, name="my_emails"),
]
