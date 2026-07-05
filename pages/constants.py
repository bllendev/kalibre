from django.conf import settings


ERROR_EMAIL_TEMPLATE_LIST = [
    'Kalibre - ERROR',                  # subject
    '',                                 # empty message line
    str(settings.DEFAULT_FROM_EMAIL),               # from email
    [email for _, email in settings.ADMINS],        # recipient_list
]
