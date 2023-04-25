# django
from django.test import TestCase, SimpleTestCase
from django.conf import settings

# local
from users.tests.factories import CustomUserFactory
from users.models import Email
from books.tests.factories import BookFactory
from books.libgen_api import LibgenSearch, SearchRequest
from books.libgen_api import LibgenAPI, LibgenBook
from books._translate import EbookTranslate
from books.models import Book
from books.tests.test_book_model import TEST_BOOK_PKL_PATH

# tools
import os
import json
import pickle
import openai
from googletrans import Translator


"""
docker compose exec web python manage.py test books.tests.test_translate --noinput --parallel --failfast
"""


class OpenAIAPITest(SimpleTestCase):
    _multiprocess_can_split_ = True
    _multiprocess_shared_ = False

    def setUp(self):
        openai.organization = "Personal"
        openai.api_key = os.getenv("OPENAI_AI_KEY")
        print(f"openai.Model.list(): {openai.Model.list()}")
        self.assertTrue(openai.Model.list())


class EbookTranslateTest(SimpleTestCase):
    _multiprocess_can_split_ = True
    _multiprocess_shared_ = False

    @classmethod
    def setUpClass(cls):
        super(EbookTranslateTest, cls).setUpClass()

        cls.book_file_path = TEST_BOOK_PKL_PATH
        print(f"self.book_file_path: {cls.book_file_path}")

        # create book obj to test
        cls.test_book = BookFactory.build(test_book=True)  # orange tree book :)

        # open and assert test book
        with open(TEST_BOOK_PKL_PATH, "rb") as f:
            cls.test_epub = pickle.load(f)

    def test_epub_load(self):
        """make sure epub is loading in"""
        self.assertTrue(self.test_epub)

    def test_google_translate_api(self):
        """
        a quick test to make sure my version of google translate api is working
        """
        test_str = Translator().translate("hello", dest="es")
        self.assertEquals(test_str.text.lower(), "hola")

    # def test_get_book_translated(self):
    #     """
    #     testing book translation (should send to dev email)
    #     ... currently only testing english to spanish
    #     ... currently only testing google translate api
    #     """
    #     self.test_book.send(email_list=["bllendev@gmail.com"], language=Email._TRANSLATE_EN_ES)
