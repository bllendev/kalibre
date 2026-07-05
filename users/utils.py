from django.core import mail
import logging

logger = logging.getLogger(__name__)


# TODO: make send_email delayed async with celery
def send_emails(
    template_message,
    file_buffer=None,
    file_name=None,
    content_type="application/octet-stream",
):
    status = None
    try:
        # send email to recipient
        with mail.get_connection() as connection:
            email_message = mail.EmailMessage(
                *tuple(template_message), connection=connection
            )

            # attach file from memory (if one was provided)
            if file_buffer:
                email_message.attach(
                    file_name, file_buffer.read(), content_type
                )
                file_buffer.seek(0)  # reset file pointer if needed again

            email_message.send(fail_silently=False)
            status = True

    except Exception as e:
        status = False
        logger.error(f"ERROR: users.utils.send_emails | {e}")
        raise e

    return status
