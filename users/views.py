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

        # -------------- #
        # -- my_email -- #
        # -------------- #
        # build email_addresses and username_str
        email_addresses = []
        username_str = ''
        if self.request.user.is_authenticated:
            username = self.request.user.username
            user = CustomUser.objects.get(username=username)
            email_addresses = user.email_addresses.all()
            username_str = f"{username}'s emails!"

        context["LANGUAGES"] = LANGUAGES
        context["email_addresses"] = email_addresses
        context["username_str"] = username_str
        return context
