import unittest
from unittest.mock import patch
from books.api.api_openlibrary import OpenLibraryAPI


"""
docker compose exec web python manage.py test books.tests.test_api_openlibrary --parallel --noinput --failfast
"""


class TestOpenLibraryAPI(unittest.TestCase):

    def setUp(self):
        self.api = OpenLibraryAPI()

    # @patch.object(OpenLibraryAPI, '_get_book_search_results')
    # def test_get_book_search_results_success(self, mock_get_book_search_results):
    #     # Mock the return value of the private method to simulate successful response
    #     mock_get_book_search_results.return_value = ["book1", "book2", "book3"]

    #     # Test
    #     result = self.api.get_book_search_results()

    #     # Assert
    #     self.assertEqual(result, ["book1", "book2", "book3"])

    # @patch.object(OpenLibraryAPI, '_get_book_search_results')
    # def test_get_book_search_results_failure(self, mock_get_book_search_results):
    #     # Mock the method to raise an exception to simulate failure scenario
    #     mock_get_book_search_results.side_effect = Exception("An error occurred!")

    #     # Test and Assert
    #     with self.assertRaises(Exception) as context:
    #         self.api.get_book_search_results()
    #     self.assertEqual(str(context.exception), "An error occurred!")
