import unittest
from unittest.mock import patch, Mock
from books.api._api_openlibrary import OpenLibraryAPI


"""
docker compose exec web python manage.py test books.tests.test_api_openlibrary --parallel --noinput --failfast
"""


class TestOpenLibraryAPI(unittest.TestCase):
    """
    """

    def setUp(self):
        self.api = OpenLibraryAPI()
    
    def test_get_book_search_results(self):
        """tests the calling of the api, leave this commented as it tests the api through a real query"""
        book_list = self.api._get_book_search_results(query="my sweet orange tree")
        
        self.assertTrue(book_list)
        self.assertTrue(f"{book_list['docs']}")

    @patch('books.api._api_openlibrary.requests.get')
    def test_get_book_search_results_success(self, mock_get):
        """"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "start": 0,
            "num_found": 1,
            "docs": [
                {
                    "title": "Test Book",
                    "author_name": ["Test Author"],
                }
            ]
        }
        mock_get.return_value = mock_response

        api = OpenLibraryAPI()
        results = api.get_book_search_results("Test Book")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Test Book")

    @patch('books.api._api_openlibrary.requests.get')
    def test_get_book_search_results_failure(self, mock_get):
        # mocking a failed response from the requests.get method
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = Exception("Not Found")
        mock_get.return_value = mock_response

        api = OpenLibraryAPI()
        with self.assertRaises(Exception) as context:
            api.get_book_search_results("Non-existent Book")
        self.assertTrue("Not Found" in str(context.exception))

    # @patch.object(OpenLibraryAPI, '_get_book_search_results')
    # def test_get_book_search_results_success(self, mock_get_book_search_results):
    #     # mock the return value of the private method to simulate successful response
    #     mock_get_book_search_results.return_value = ["book1", "book2", "book3"]

    #     # test
    #     result = self.api.get_book_search_results()

    #     # assert
    #     self.assertEqual(result, ["book1", "book2", "book3"])

    # @patch.object(OpenLibraryAPI, '_get_book_search_results')
    # def test_get_book_search_results_failure(self, mock_get_book_search_results):
    #     # mock the method to raise an exception to simulate failure scenario
    #     mock_get_book_search_results.side_effect = Exception("An error occurred!")

    #     # aest and assert
    #     with self.assertRaises(Exception) as context:
    #         self.api.get_book_search_results()
    #     self.assertEqual(str(context.exception), "An error occurred!")
