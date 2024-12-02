import copy
import urllib
import io

from books.constants import EMAIL_TEMPLATE_LIST
from users.utils import send_emails
import logging

logger = logging.getLogger(__name__)


def send_gutenberg_book(book_title, link, emails, language):
    file_buffer = None
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

            if file_buffer:
                msg = copy.deepcopy(EMAIL_TEMPLATE_LIST)
                msg[3] = emails
                status = send_emails(msg, file_buffer, book_title)

    except Exception as e:
        logger.error(e)
        raise e

    status = False
    if file_buffer:
        msg = copy.deepcopy(EMAIL_TEMPLATE_LIST)
        msg[3] = emails
        status = send_emails(msg, file_buffer, book_title)

    return status
