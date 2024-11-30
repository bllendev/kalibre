from decouple import config
from books.constants import EMAIL_TEMPLATE_LIST
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


def _create_book_file(json_links, language):
    """
    creates book file from links, will translate if needed

    params:
        - language: language to translate to (if needed)
    returns:
        - path to saved book file (translated if needed)
    """
    # get book file content
    book_link = None
    for link in json_links:
        try:
            with urllib.request.urlopen(link) as response:
                soup = BeautifulSoup(response.read(), "html.parser")
                book_links = soup.find_all("a")
                for link in book_links:
                    book_link = link.get("href")

                    # validate book file type
                    valid_book_file_type = any(
                        [
                            "epub" in book_link,
                            "mobi" in book_link,
                            "pdf" in book_link,
                        ]
                    )
                    if not valid_book_file_type:
                        raise TypeError(
                            f"File must be pdf, epub, or mobi... {book_link}"
                        )

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
        except Exception as e:
            print(f"error sending book... {e}")
            continue


def _convert_book_file(book_file_path, convert_output_format):
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
        # optionally, handle the file response, e.g., save it to disk
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


def get_book_file_path(json_links, language=None, convert_output_format=""):
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
        # if convert_output_format:
        #     book_file_buffer = _convert_book_file(
        #         book_file_buffer, convert_output_format
        #     )
    except Exception as e:
        logging.error(f"Error processing book file: {e}")
        raise e

    return book_file_buffer


def send_libgen_book(book_title, json_links, emails, language):
    book_file_buffer = get_book_file_path(json_links, language)

    status = False
    if book_file_buffer:
        msg = copy.deepcopy(EMAIL_TEMPLATE_LIST)
        msg[3] = emails
        status = send_emails(msg, book_file_buffer, book_title)

    return status
