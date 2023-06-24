from django.urls import path, include
from rest_framework.routers import DefaultRouter

from books import views
from books import ajax


# leave disabled until react is fully implemented -@AG
# router = DefaultRouter()
# router.register('', views.BookViewSet)


urlpatterns = [
    # core views
    # path('', include(router.urls)),
    path('<uuid:pk>', views.BookDetailView.as_view(), name='book_detail'),
    path('search_results/', views.search_results, name='search_results'),
    path("my_emails/", views.my_emails, name="my_emails"),

    # ajax
    path("send-book-ajax/", ajax.send_book_ajax, name="send_book_ajax"),
    path("add-email/", ajax.add_email, name="add_email"),
    path("delete-email", ajax.delete_email, name="delete_email"),
    path("toggle-translate-email", ajax.toggle_translate_email, name="toggle_translate_email")
]
