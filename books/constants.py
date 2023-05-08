from django.conf import settings
import os


AI_PROMPT = "Hello AI Librarian! I am looking for a new book to read, "
AI_PROMPT += "but I am not sure what I want. Can you please ask me "
AI_PROMPT += "pertinent questions about my preferences for books, authors, "
AI_PROMPT += "time periods, genres, and any other relevant factors "
AI_PROMPT += "to help me discover the perfect book to read next? Ask no more "
AI_PROMPT += "than 4 questions. "


# UTILITY CONSTANTS
EMAIL_TEMPLATE_LIST = [
    '',                      # empty subject line
    '',                  # empty message line
    str(settings.DEFAULT_FROM_EMAIL),        # from email
    list(),                             # recipient_list
]