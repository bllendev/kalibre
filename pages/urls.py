from django.urls import path
from pages.views import (
    AboutPageView,
    home,
)


urlpatterns = [
    path("about/", AboutPageView.as_view(), name="about"),  # new
    path("", home, name="home"),
]
