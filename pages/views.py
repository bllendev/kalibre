# django
import sys
import traceback
from django.views.generic import TemplateView
from django.views.decorators.cache import never_cache
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.http import HttpResponseBadRequest, HttpResponseForbidden, HttpResponseServerError
from django.conf import settings

# logger
import logging
logger = logging.getLogger(__name__)

# local
from ai.constants import AI_PROMPT
from pages.constants import ERROR_EMAIL_TEMPLATE_LIST
from books.utils import send_emails


@method_decorator(never_cache, name='dispatch')
class HomePageView(TemplateView):
    template_name = "home.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['AI_PROMPT'] = AI_PROMPT
        return context


class AboutPageView(TemplateView):
    template_name = "about.html"


# ----------------- #
# -- error views -- #
# ----------------- #
def handler500(request):
    context = {
        'title': '500 - Internal Server Error',
        'error_description': 'There was an unexpected error processing your request.',
        'todo_description': 'Please try again later or contact our support team.',
    }

    # get exception info
    exc_type, exc_value, exc_traceback = sys.exc_info()
    exception_traceback = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    error_str = f'Internal Server Error: {request.path}\n{exception_traceback}'

    # log the complete traceback
    logger.error(error_str, extra={'status_code': 500, 'request': request})

    # TODO: implement send_emails
    if True or settings.ENVIRONMENT == "production":
        template_message = copy.deepcopy(ERROR_EMAIL_TEMPLATE_LIST)
        template_message[1] = error_str
        status = send_emails(template_message)

    response = HttpResponseServerError(render(request, 'error_page.html', context))
    response.status_code = 500
    return response

    return HttpResponseServerError(render(request, 'error_page.html', context))


def handler404(request, exception):
    context = {
        'title': '404 - Not Found',
        'error_description': 'Hmm, seems like this page does not exist!',
        'todo_description': 'Please check the URL or navigate back to the homepage.',
    }
    return render(request, 'error_page.html', context)


def handler400(request, exception):
    context = {
        'title': '400 - Bad Request',
        'error_description': 'Hmm, this seems like a bad request!',
        'todo_description': 'Please ensure the request is correct or contact our support team.',
    }
    return HttpResponseBadRequest(render(request, 'error_page.html', context))


def handler403(request, exception):
    context = {
        'title': '403 - Forbidden',
        'error_description': 'Sorry, you do not have permission to access this page.',
        'todo_description': 'If you think this is an error, please contact our support team.',
    }
    return HttpResponseForbidden(render(request, 'error_page.html', context))
