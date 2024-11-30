from decouple import config
from bs4 import BeautifulSoup
import copy
import requests
import urllib
import os
import io

from books.constants import EMAIL_TEMPLATE_LIST
from users.utils import send_emails
import logging

logger = logging.getLogger(__name__)


def _create_book_file(link, language):
    """
    creates book file from links, will translate if needed

    params:
        - language: language to translate to (if needed)
    returns:
        - path to saved book file (translated if needed)
    """
    try:
        with urllib.request.urlopen(link) as response:
            if response.status != 200:
                raise RuntimeError("Failed to download book file")

            # read the content of the response
            file_content = response.read()
            if not file_content:
                raise RuntimeError("No content retrieved from the link")

            # keep the file in an in-memory buffer
            file_buffer = io.BytesIO(file_content)

            # # TRANSLATE FEATURE UNDER CONSTRUCTION FOR NOW @AG++
            # if language and language != "en":
            #     ebook_translate = EbookTranslate(new_file_path, language, google_api=True)
            #     new_file_path = ebook_translate.get_translated_book_path()

            return file_buffer

    except Exception as e:
        print(f"Error sending book... {e}")
        raise e


def get_book_file_path(json_links, language=None):
    """
    handles the process of creating and optionally converting a book file.

    params:
        - language: Language for translation.
        - convert_output_format: Format to convert the book file format.

    returns:
        path to the processed book file.
    """
    try:
        book_file_buffer = _create_book_file(json_links, language)
    except Exception as e:
        logging.error(f"Error processing book file: {e}")
        raise e
    return book_file_buffer


def send_gutenberg_book(book_title, link, emails, language):
    book_file_buffer = get_book_file_path(link, language)

    status = False
    if book_file_buffer:
        msg = copy.deepcopy(EMAIL_TEMPLATE_LIST)
        msg[3] = emails
        status = send_emails(msg, book_file_buffer, book_title)

    return status
