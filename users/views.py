from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth import get_user_model
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator

from users.forms import CustomUserCreationForm

from translate.constants import LANGUAGES


CustomUser = get_user_model()


class SignupPageView(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "accounts/signup.html"


@method_decorator(never_cache, name='dispatch')
class MyProfile(generic.TemplateView):
    template_name = "users/my_profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        username = self.request.user.username  # view is inaccessible without user login
        user = CustomUser.objects.get(username=username)

        # -------------- #
        # -- my_books -- #
        # -------------- #
        # context["my_books"] = user.my_books.all()  TODO: implement new foreignkey

        # -------------- #
        # -- my_email -- #
        # -------------- #
        context["LANGUAGES"] = LANGUAGES
        context["email_addresses"] = user.email_addresses.all()
        context["username_str"] = f"{username}'s emails!"
        return context
