import os
from django.db import transaction
from django.shortcuts import redirect
from django.core import mail

from ai.models import Message

# import nltk
# # from textblob import TextBlob
# from nltk.corpus import stopwords
# from nltk.tokenize import word_tokenize
# from nltk.stem import PorterStemmer
import string
import openai

import logging

logger = logging.getLogger(__name__)


# # Download required resources
# nltk.download('stopwords')
# nltk.download('punkt')
# nltk.download('wordnet')
# nltk.download('averaged_perceptron_tagger')


# Define function to normalize a word
def process_text(word):
    # Remove punctuation and convert to lowercase
    normalized_word = word.translate(str.maketrans("", "", string.punctuation)).lower()
    return normalized_word


# # Define function to stem a word
# def stem_word(word):
#     stemmer = PorterStemmer()
#     stemmed_word = stemmer.stem(word)
#     return stemmed_word


@transaction.atomic
def bulk_save(queryset):
    """atomic save! prevent save issues when saving to db"""
    for item in queryset:
        item.save()


def send_emails(template_message, file_buffer, file_name):
    status = None
    try:
        # send book as email to recipient
        with mail.get_connection() as connection:
            email_message = mail.EmailMessage(*tuple(template_message), connection=connection)

            if not file_buffer:
                raise ValueError("file_buffer is None")

            # attach file from memory
            email_message.attach(file_name, file_buffer.read(), 'application/octet-stream')
            file_buffer.seek(0)  # Reset file pointer if needed again

            email_message.send(fail_silently=False)
            status = True

    except Exception as e:
        status = False
        logger.error(f"ERROR: books.utils.send_emails | {e}")
        raise e

    return status


def os_silent_remove(filename):
    try:
        os.remove(filename)
    except OSError as e:
        logger.warning(f"ERROR: books.utils.os_silent_remove | {e}")


def fx_return_to_sender(request, remove_GET=True):
    """
        Return user back to the url from whence they came.
    """
    request_http_referer = request.META.get("HTTP_REFERER", "")
    if request_http_referer and "?" in request_http_referer and remove_GET:
        request_http_referer = request_http_referer.split("?")[0]
    return redirect(request_http_referer)


def request_is_ajax_bln(request):
    return request.headers.get('HX-Request') == 'true'