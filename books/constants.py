from django.conf import settings
import os


AI_PROMPT = "Hello AI Librarian! I am looking for a new book to read, "
AI_PROMPT += "but I am not sure what I want. Can you please ask me "
AI_PROMPT += "pertinent questions about my preferences for books, authors, "
AI_PROMPT += "time periods, genres, and any other relevant factors "
AI_PROMPT += "to help me discover the perfect book to read next? Ask no more "
AI_PROMPT += "than 4 questions. Continue asking questions until we narrow "
AI_PROMPT += "down the search to a few books, then present the best books "
AI_PROMPT += "to me with a short description of each. "


# UTILITY CONSTANTS
EMAIL_TEMPLATE_LIST = [
    '',                      # empty subject line
    '',                  # empty message line
    str(settings.DEFAULT_FROM_EMAIL),        # from email
    list(),                             # recipient_list
]