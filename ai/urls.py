from django.urls import path
from ai import ajax


urlpatterns = [
    # ajax
    path("ai-librarian/", ajax.ai_librarian, name="ai_librarian"),
]
