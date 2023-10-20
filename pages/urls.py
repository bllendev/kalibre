from django.urls import path
from pages.views import (
    AboutPageView,
    HomePageView,
)


urlpatterns = [
    path("about/", AboutPageView.as_view(), name="about"),
    path("", HomePageView.as_view(), name="home"),
]
