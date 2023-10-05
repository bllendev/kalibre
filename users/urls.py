from django.urls import path
from users.views import MyProfile


urlpatterns = [
    path("my-profile/", MyProfile.as_view(), name="my_profile"),
]