from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.core.mail import EmailMessage
from django.shortcuts import render
from libgen_api import LibgenSearch
import urllib.request
import os
import ast
from .helpers import validate_email, iterate_download_links, save_file_in_media_root, delete_file


def partial_search(request):
    """
    Perform a search using the LibgenSearch class and return the results as a partial.
    """
    if request.htmx:
        s = LibgenSearch()
        title = request.GET.get("title")
        author = request.GET.get("author")
        extension = request.GET.get("extension")

        if title is None or (title == "" and author == "" and extension == ""): # initial page load
            results = []
        elif len(title) >= 3 and author == "" and extension == "": # title search
            results = s.search_title(title)
        elif len(title) > 3 and (author != "" or extension != ""): # filtered title search 
            title_filters = {"Author": author, "Extension": extension}
            results = s.search_title_filtered(title, title_filters, exact_match=False)
        elif len(title) < 3 and author != "" and extension == "": # author search
            results = s.search_author(author)
        elif len(title) < 3 and author != "" and extension != "": # filtered author search
            author_filters = {"Extension": extension}
            results = s.search_author_filtered(author, author_filters, exact_match=False)

        stored_kindle_email = request.session.get("kindle_email")

        context = {
            "books": results,
            "stored_kindle_email": stored_kindle_email
        }
        return render(request, "emailer/partial_results.html", context)
    return render(request, "emailer/partial_search.html")

def send_to_kindle(request):
    """
    Send the selected book to the Kindle email address.
    """
    if request.method == "POST":
        item_to_download = ast.literal_eval(request.POST.get("book_to_download")) # convert string to dict
        kindle_email = request.POST.get("kindle_email")
        print(f"Kindle email: {kindle_email}")

        # Server-side email validation
        if len(kindle_email) == 0:
            print("No email address provided.")
            return HttpResponse("No email address provided.")
        elif not validate_email(kindle_email):
            print("Invalid email address.")
            return HttpResponse("Invalid email address.")

        # resolve_download_links()
        try:
            s = LibgenSearch() 
            url = s.resolve_download_links(item_to_download)
        except Exception as e:
            # Handle the exception or log the error message
            print(f"Failed to resolve download links: {str(e)}")
            return HttpResponse("Failed to resolve download links.")

        # Iterate through the download links
        response = iterate_download_links(url)

        # Set the filename and destination directory
        filename = os.path.basename(item_to_download['Title'] + '.' + item_to_download['Extension'])
        destination_directory = settings.MEDIA_ROOT
        file_path = os.path.join(destination_directory, filename)
        print(f"File path: {file_path}")

        # Save the file in MEDIA_ROOT
        if save_file_in_media_root(response, file_path):
            print("File saved successfully in MEDIA_ROOT.")
        else:
            return HttpResponse("Failed to save the file.")

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
            success = True
        except Exception:
            success = False

        delete_file(file_path)
        return JsonResponse({'success': success})



