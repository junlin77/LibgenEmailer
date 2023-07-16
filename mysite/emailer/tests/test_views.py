from django.test import TestCase, Client, RequestFactory
from django.urls import reverse

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
        self.factory = RequestFactory()

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

