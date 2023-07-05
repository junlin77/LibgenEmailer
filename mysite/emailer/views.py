from django.http import HttpResponse
import urllib.request
import os
from django.conf import settings
from django.core.mail import EmailMessage
from django.shortcuts import render
from libgen_api import LibgenSearch
from django.views.decorators.csrf import csrf_exempt
import ast

def index(request):
    s = LibgenSearch()
    title = request.GET.get("title")
    if title is None:
        results = []
    else:
        results = s.search_title(title)
    books = {"books": results}
    return render(request, "emailer/index.html", books)

@csrf_exempt
def send_to_kindle(request):
    if request.method == "POST":
        item_to_download = request.POST.get("book_to_download")
        item_to_download = ast.literal_eval(item_to_download) # convert string to dict
        kindle_email = request.GET.get("kindle_email")
        print(kindle_email)
        # resolve_download_links()
        s = LibgenSearch()
        
        url = s.resolve_download_links(item_to_download)

        # TODO: add logic to try other link if failed
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
        email.send()

        # TODO: verify if email sent successfully 

        # Delete the temporary file
        os.remove(file_path)

        # Check if the file has been successfully deleted
        if not os.path.exists(file_path):
            print("File deleted successfully from MEDIA_ROOT.")
        else:
            print("Failed to delete the file in MEDIA_ROOT.")

    return HttpResponse("Email sent successfully.")