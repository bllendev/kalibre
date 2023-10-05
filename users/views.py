from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth import get_user_model
from users.forms import CustomUserCreationForm


CustomUser = get_user_model()


class SignupPageView(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "accounts/signup.html"



class MyProfile(generic.TemplateView):
    template_name = "my_profile.html"
