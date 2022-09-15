from django.urls import path

from accounts import views


urlpatterns = [
    path("signup/", views.SignupPageView.as_view(), name="signup"),
]