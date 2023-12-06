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
    path('search-results/', views.search_results, name='search_results'),

    # ajax
    path("send-book-ajax/<uuid:pk>/", ajax.send_book_ajax, name="send_book_ajax"),
]
