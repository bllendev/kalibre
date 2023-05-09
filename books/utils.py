import os
from django.db import transaction
from django.shortcuts import redirect

# import nltk
# # from textblob import TextBlob
# from nltk.corpus import stopwords
# from nltk.tokenize import word_tokenize
# from nltk.stem import PorterStemmer
import string


# # Download required resources
# nltk.download('stopwords')
# nltk.download('punkt')
# nltk.download('wordnet')
# nltk.download('averaged_perceptron_tagger')


# Define function to normalize a word
def process_text(word):
    # Remove punctuation and convert to lowercase
    normalized_word = word.translate(str.maketrans("", "", string.punctuation)).lower()
    return normalized_word


# # Define function to stem a word
# def stem_word(word):
#     stemmer = PorterStemmer()
#     stemmed_word = stemmer.stem(word)
#     return stemmed_word


@transaction.atomic
def bulk_save(queryset):
    """atomic save! prevent save issues when saving to db"""
    for item in queryset:
        item.save()


def os_silent_remove(filename):
    try:
        os.remove(filename)
    except OSError as e:
        print(f"os_silent_remove: {e}")


def fx_return_to_sender(request, remove_GET=True):
    """
        Return user back to the url from whence they came.
    """
    request_http_referer = request.META.get("HTTP_REFERER", "")
    if request_http_referer and "?" in request_http_referer and remove_GET:
        request_http_referer = request_http_referer.split("?")[0]
    return redirect(request_http_referer)
