from django.test import TestCase, Client
from django.urls import reverse
from django.http import HttpResponse
from unittest.mock import patch, MagicMock
from emailer.helpers import iterate_download_links 

class PartialSearchTestCase(TestCase):

    def setUp(self):
        self.client = Client()

    def test_empty_search(self):
        response = self.client.get(reverse('partial_search'))
        self.assertEqual(response.status_code, 200)

    def test_title_search(self):
        response = self.client.get(reverse('partial_search'), {'title': 'Test Title'})
        self.assertEqual(response.status_code, 200)

    def test_filtered_title_search(self):
        response = self.client.get(reverse('partial_search'), {'title': 'Test Title', 'author': 'Test Author', 'extension': 'pdf'})
        self.assertEqual(response.status_code, 200)

    def test_author_search(self):
        response = self.client.get(reverse('partial_search'), {'author': 'Test Author'})
        self.assertEqual(response.status_code, 200)

    def test_filtered_author_search(self):
        response = self.client.get(reverse('partial_search'), {'author': 'Test Author', 'extension': 'pdf'})
        self.assertEqual(response.status_code, 200)

    def test_invalid_search(self):
        response = self.client.get(reverse('partial_search'), {'title': 'T'})
        self.assertEqual(response.status_code, 200)

    def test_email_input_only(self):
        response = self.client.get(reverse('partial_search'), {'kindle_email': 'test@kindle.com'})
        self.assertEqual(response.status_code, 200)
        
    def test_render_partial_search_templates(self):
        response = self.client.get(reverse('partial_search'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'emailer/partial_results.html')
        self.assertTemplateUsed(response, 'emailer/partial_search.html')

class SendToKindleTestCase(TestCase):

    def setUp(self):
        self.client = Client()

    def test_valid_email_address(self):
        response = self.client.post(reverse('send_to_kindle'), {
            'book_to_download': '{"ID": "123", "Title": "Book Title"}',
            'kindle_email': 'test@example.com'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Failed to resolve download links.") # As book doesn't exist

    def test_invalid_email_address(self):
        response = self.client.post(reverse('send_to_kindle'), {
            'book_to_download': '{"ID": "123", "Title": "Book Title"}',
            'kindle_email': 'invalid_email'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid email address.")

    def test_no_email_address(self):
        response = self.client.post(reverse('send_to_kindle'), {
            'book_to_download': '{"ID": "123", "Title": "Book Title"}',
            'kindle_email': ''
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No email address provided.")

    @patch('urllib.request.urlopen')
    def test_failed_iterate_download(self, mock_urlopen):
        # Mock the urlopen function to raise an exception for all URLs
        mock_urlopen.side_effect = Exception('Failed to download from all URLs.')

        # Create a mock URL dictionary
        url = {
            "key1": "http://example.com/url1",
            "key2": "http://example.com/url2"
        }

        # Call the function under test
        response = iterate_download_links(url)

        # Assert that the function returns an HttpResponse with the expected message
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "Failed to download from all URLs.")

        # Assert that urlopen was called with the correct URLs
        mock_urlopen.assert_any_call("http://example.com/url1")
        mock_urlopen.assert_any_call("http://example.com/url2")

    # @patch('libgen.LibgenSearch')
    # @patch('path.to.urllib.request.urlopen')
    # def test_mocking_libgen_search_and_urlopen(self, mock_urlopen, mock_libgen_search):
    #     # Mock the LibgenSearch and urllib.request.urlopen
    #     mock_urlopen.return_value = MagicMock()
    #     mock_libgen_search.return_value = MagicMock()

    #     response = self.client.post(reverse('send_to_kindle'), {
    #         'book_to_download': '{"ID": "123", "Title": "Book Title"}',
    #         'kindle_email': 'test@example.com'
    #     })
    #     self.assertEqual(response.status_code, 200)
    #     # Add assertions for the expected response

    # @patch('path.to.save_file_in_media_root')
    # @patch('path.to.delete_file')
    # def test_mocking_save_file_and_delete_file(self, mock_delete_file, mock_save_file):
    #     mock_save_file.return_value = True
    #     mock_delete_file.return_value = True

    #     response = self.client.post(reverse('send_to_kindle'), {
    #         'book_to_download': '{"ID": "123", "Title": "Book Title"}',
    #         'kindle_email': 'test@example.com'
    #     })
    #     self.assertEqual(response.status_code, 200)
    #     # Add assertions for the expected response

    # @patch('path.to.EmailMessage')
    # def test_mocking_email_message(self, mock_email_message):
    #     mock_email_message.return_value = MagicMock()
    #     email_instance = mock_email_message.return_value
    #     email_instance.attach_file.return_value = True
    #     email_instance.send.return_value = True

    #     response = self.client.post(reverse('send_to_kindle'), {
    #         'book_to_download': '{"ID": "123", "Title": "Book Title"}',
    #         'kindle_email': 'test@example.com'
    #     })
    #     self.assertEqual(response.status_code, 200)
    #     # Add assertions for the expected response
