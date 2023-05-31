# django
from django.views.generic import TemplateView
from django.views.decorators.cache import never_cache
from django.shortcuts import render

# local
from ai.constants import AI_PROMPT


@never_cache
def home(request):
    """returns: home page view"""
    return render(
        request,
        'home.html',
        {
            'AI_PROMPT': AI_PROMPT,
        })


class AboutPageView(TemplateView):
    template_name = "about.html"
