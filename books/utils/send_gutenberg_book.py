import copy
import urllib
import io

from books.constants import EMAIL_TEMPLATE_LIST
from users.utils import send_emails
import logging

logger = logging.getLogger(__name__)


# (url token, file extension, mime type) - checked in order, first match wins
# ... more specific tokens (e.g. "epub.zip") must come before generic ones ("epub")
FILE_TYPES = [
    ("pdf", ".pdf", "application/pdf"),
    ("epub.zip", ".zip", "application/zip"),
    ("epub", ".epub", "application/epub+zip"),
    ("kindle", ".mobi", "application/x-mobipocket-ebook"),
    ("mobi", ".mobi", "application/x-mobipocket-ebook"),
    ("txt", ".txt", "text/plain"),
    ("text", ".txt", "text/plain"),
    ("html", ".html", "text/html"),
]


def get_file_type(link):
    """derive (extension, mime_type) from a gutenberg resource url
    ... so the emailed attachment keeps a usable file extension.
    """
    link_lower = link.lower()
    for token, extension, mime_type in FILE_TYPES:
        if token in link_lower:
            return extension, mime_type
    return "", "application/octet-stream"


def send_gutenberg_book(book_title, link, emails, language):
    file_buffer = None
    extension, mime_type = get_file_type(link)
    file_name = f"{book_title}{extension}"
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

    except Exception as e:
        logger.error(e)
        raise e

    status = False
    if file_buffer:
        msg = copy.deepcopy(EMAIL_TEMPLATE_LIST)
        msg[3] = emails
        status = send_emails(msg, file_buffer, file_name, mime_type)

    return status
