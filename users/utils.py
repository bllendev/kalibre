from django.core import mail
import logging

logger = logging.getLogger(__name__)


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
        logger.error(f"ERROR: users.utils.send_emails | {e}")
        raise e

    return status
