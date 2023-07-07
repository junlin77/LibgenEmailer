from django.http import HttpResponse
import urllib.request
import os
from django.conf import settings
from django.core.mail import EmailMessage
from django.shortcuts import render
from libgen_api import LibgenSearch
from django.views.decorators.csrf import csrf_exempt
import ast
import re
from django.http import JsonResponse

def index(request):
    s = LibgenSearch()
    title = request.GET.get("title")
    author = request.GET.get("author")
    extension = request.GET.get("extension")

    if title is None: # initial page load
        results = []
    elif len(title) > 3 and author == "" and extension == "": # title search
        results = s.search_title(title)
    elif len(title) > 3 and (author != "" or extension != ""): # filtered title search 
        title_filters = {"Author": author, "Extension": extension}
        results = s.search_title_filtered(title, title_filters, exact_match=False)
    elif len(title) <= 3 and author != "" and extension == "": # author search
        results = s.search_author(author)
    elif len(title) <= 3 and author != "" and extension != "": # filtered author search
        author_filters = {"Extension": extension}
        results = s.search_author_filtered(author, author_filters, exact_match=False)

    books = {"books": results}
    return render(request, "emailer/index.html", books)

@csrf_exempt
def send_to_kindle(request):
    if request.method == "POST":
        item_to_download = request.POST.get("book_to_download")
        item_to_download = ast.literal_eval(item_to_download) # convert string to dict
        kindle_email = request.POST.get("kindle_email")
        print(kindle_email)

        # Server-side email validation
        if not validate_email(kindle_email):
            return HttpResponse("Invalid email address.")

        # resolve_download_links()
        s = LibgenSearch()
        
        url = s.resolve_download_links(item_to_download)

        # TODO: add logic to try other link if failed
        # Get the Cloudflare link
        url = url['Cloudflare']

        # Send a GET request to download the file
        response = urllib.request.urlopen(url)

        filename = os.path.basename(item_to_download['Title'] + '.' + item_to_download['Extension'])

        # Get the Django default file saving directory
        destination_directory = settings.MEDIA_ROOT

        # Create the absolute path to save the file
        file_path = os.path.join(destination_directory, filename)

        # Save the file to the destination directory
        with open(file_path, 'wb') as file:
            file.write(response.read())

        # Check if the file has been successfully saved
        if os.path.exists(file_path):
            print("File saved successfully in MEDIA_ROOT.")
        else:
            print("Failed to save the file in MEDIA_ROOT.")

        # Send the file as an email attachment
        email = EmailMessage(
            'Send to Kindle Test',
            'Please find the attached file.',
            settings.DEFAULT_FROM_EMAIL,
            [kindle_email],
        )
        email.attach_file(file_path)

        try:
            email.send()
            # Delete the temporary file
            delete_file(file_path)
            return JsonResponse({'success': True})
        except:
            # Delete the temporary file
            delete_file(file_path)
            return JsonResponse({'success': False})

def validate_email(email):
    """
    Perform server-side validation on the email address.
    Returns True if the email is valid, False otherwise.
    """
    # Basic email format validation using regex
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        return False
    return True

def delete_file(file_path):
    try:
        os.remove(file_path)
        # Check if the file has been successfully removed
        if not os.path.exists(file_path):
            print("File deleted successfully.")
        else:
            print("Failed to delete the file.")
    except OSError as e:
        print(f"Error deleting the file: {str(e)}")
