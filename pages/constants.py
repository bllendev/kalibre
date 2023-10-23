from django.conf import settings


ERROR_EMAIL_TEMPLATE_LIST = [
    'Kalibre - ERROR',                  # subject
    '',                                 # empty message line
    str(settings.DEFAULT_FROM_EMAIL),   # from email
    list(settings.DEFAULT_FROM_EMAIL),  # recipient_list
]
