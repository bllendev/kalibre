# django
from django.test import SimpleTestCase

# local
from books.tests.factories import BookFactory
from translate._translate import Translate
from translate.constants import LANGUAGES
from books.tests.test_book_model import TEST_BOOK_PKL_PATH

# tools
import pickle


"""
docker compose exec web python manage.py test translate.tests.test_translate --noinput --parallel --failfast
"""


class TranslateConstants(SimpleTestCase):
    def test_langauge_constants(self):
        self.assertTrue(len(LANGUAGES) == 105)


class TranslateTest(SimpleTestCase):
    def setUp(self):
        self.test_translator = Translate()

    def test_init(self):
        # assert init true
        self.assertTrue(self.test_translator)

        # assert google api is default used
        self.assertTrue(self.test_translator.google_api)

    def test_google_translate_correct_translation(self):
        text = self.test_translator.translate_text("hello", language="es")
        self.assertEquals(text.lower(), "hola")


class EbookTranslateTest(SimpleTestCase):
    _multiprocess_can_split_ = True
    _multiprocess_shared_ = False

    @classmethod
    def setUpClass(cls):
        super(EbookTranslateTest, cls).setUpClass()

        cls.book_file_path = TEST_BOOK_PKL_PATH

        # create book obj to test
        cls.test_book = BookFactory.build(test_book=True)  # orange tree book :)

        # open and assert test book
        with open(TEST_BOOK_PKL_PATH, "rb") as f:
            cls.test_epub = pickle.load(f)

    def test_epub_load(self):
        """make sure epub is loading in"""
        self.assertTrue(self.test_epub)
