from django.urls import path
from users.views import SignupPageView


urlpatterns = [
    path('signup/', SignupPageView.as_view(), name='signup'),

]