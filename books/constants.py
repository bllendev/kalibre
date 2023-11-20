from django.conf import settings


# UTILITY CONSTANTS
EMAIL_TEMPLATE_LIST = [
    '',                      # empty subject line
    '',                  # empty message line
    str(settings.DEFAULT_FROM_EMAIL),        # from email
    list(),                             # recipient_list
]

# EBOOK CONVERT CONSTANTS
EBOOK_CONVERT = (
    ("pdf", "PDF"),
    ("epub", "EPUB"),
    ("mobi", "MOBI"),
)
