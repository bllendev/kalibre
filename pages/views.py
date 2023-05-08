from django.views.generic import TemplateView
from django.views.decorators.cache import never_cache
from django.shortcuts import render


# class HomePageView(TemplateView):
#     template_name = "home.html"


@never_cache
def home(request):
    """returns: home page view"""
    return render(request, 'home.html')


class AboutPageView(TemplateView):  # new
    template_name = "about.html"
