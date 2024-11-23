from django.db import transaction
from django.shortcuts import redirect
from django.core import mail
from decouple import config
from bs4 import BeautifulSoup
import requests
import urllib
import os
import io
# import nltk
# # from textblob import TextBlob
# from nltk.corpus import stopwords
# from nltk.tokenize import word_tokenize
# from nltk.stem import PorterStemmer

import logging

logger = logging.getLogger(__name__)


# # Download required resources
# nltk.download('stopwords')
# nltk.download('punkt')
# nltk.download('wordnet')
# nltk.download('averaged_perceptron_tagger')


# TODO: make send_email delayed async with celery
def send_emails(template_message, file_buffer, file_name):
    status = None
    try:
        # send book as email to recipient
        with mail.get_connection() as connection:
            email_message = mail.EmailMessage(
                *tuple(template_message), connection=connection
            )

            if not file_buffer:
                raise ValueError("file_buffer is None")

            # attach file from memory
            email_message.attach(
                file_name, file_buffer.read(), "application/octet-stream"
            )
            file_buffer.seek(0)  # reset file pointer if needed again

            email_message.send(fail_silently=False)
            status = True

    except Exception as e:
        status = False
        logger.error(f"ERROR: books.utils.send_emails | {e}")
        raise e

    return status


# TODO: remove ajax for htmx
def request_is_ajax_bln(request):
    return request.headers.get("HX-Request") == "true"


def _create_book_file(book, language):
    """
    creates book file from links, will translate if needed

    params:
        - language: language to translate to (if needed)
    returns:
        - path to saved book file (translated if needed)
    """
    # get book file content
    book_link = None
    for link in book.json_links:
        with urllib.request.urlopen(link) as response:
            soup = BeautifulSoup(response.read(), "html.parser")
            book_link = soup.find_all("a")[1].get("href")

        # break out of loop early if book_link exists
        if book_link:
            break

    # validate book_link
    if not book_link:
        raise RuntimeError("No Book Link Found to Download the book")

    # validate book file type
    valid_book_file_type = any(
        [
            book.BOOK_FILETYPE_EPUB in book_link,
            book.BOOK_FILETYPE_MOBI in book_link,
            book.BOOK_FILETYPE_PDF in book_link,
        ]
    )
    if not valid_book_file_type:
        raise TypeError(
            f"Book File Boolean must be pdf, epub, or mobi... {book_link}")

    # save og file in memory buffer (used as reference for translation as well)
    response = requests.get(book_link)
    if response.status_code != 200:
        raise RuntimeError("Failed to download book file")

    # keep the file in an in-memory buffer
    file_buffer = io.BytesIO(response.content)

    # # TRANSLATE FEATURE UNDER CONSTRUCTION FOR NOW @AG++
    # if language and language != "en":
    #     ebook_translate = EbookTranslate(new_file_path, language, google_api=True)
    #     new_file_path = ebook_translate.get_translated_book_path()

    return file_buffer


def _convert_book_file(book, book_file_path, convert_output_format):
    """
    converts the book file format using an external microservice.

    params:
        - book_file_path: Path to the book file to be converted
        - convert_output_format: The desired output format (ex: epub, pdf)

    returns:
        Path to the converted book file.
    """
    base_url = config("KALIBRE_EBOOK_CONVERT_URL")
    api_endpoint = "api/convert/"
    url = f"{base_url}{api_endpoint}?output_format={convert_output_format}"
    headers = {"X-API-Key": config("KALIBRE_PRIVADO")}

    # ensure the file exists
    if not os.path.isfile(book_file_path):
        raise RuntimeError(f"File not found: {book_file_path}")

    # prepare the file to be uploaded
    with open(book_file_path, "rb") as f:
        files = {"input_file": (os.path.basename(book_file_path), f)}
        response = requests.post(url, headers=headers, files=files)

    # handle the response
    output_path = f"output.{convert_output_format}"
    if response.status_code == 200:
        # Optionally, handle the file response, e.g., save it to disk
        with open(output_path, "wb") as out:
            out.write(response.content)
        logging.info("Success: File converted and saved.")
    else:
        logging.error("Error:", response.status_code, response.text)
        raise RuntimeError(
            f"""could not convert book_file !
                {book_file_path} | {convert_output_format}
            """
        )

    return output_path


def get_book_file_path(book, language=None, convert_output_format=""):
    """
    handles the process of creating and optionally converting a book file.

    params:
        - language: Language for translation.
        - convert_output_format: Format to convert the book file format.

    returns:
        path to the processed book file.
    """
    try:
        book_file_buffer = book._create_book_file(language)
        if convert_output_format:
            book_file_buffer = _convert_book_file(
                book, book_file_buffer, convert_output_format
            )
    except Exception as e:
        logging.error(f"Error processing book file: {e}")
        raise e

    return book_file_buffer
