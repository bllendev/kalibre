from django.urls import path
from books import views
from books import ajax


urlpatterns = [
    path('', views.BookListView.as_view(), name='book_list'),
    path('<uuid:pk>', views.BookDetailView.as_view(), name='book_detail'),
    path('search_results/', views.search_results, name='search_results'),

    # email
    path("my_emails/", views.my_emails, name="my_emails"),

    # ajax
    path("send_book/", ajax.send_book, name="send_book"),
    path("add_email/", ajax.add_email, name="add_email"),
    path("delete_email", ajax.delete_email, name="delete_email"),

]
