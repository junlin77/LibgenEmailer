import os
import re

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

def save_file_in_media_root(response, file_path):
    """
    Save the file in MEDIA_ROOT.
    """
    with open(file_path, 'wb') as file:
        file.write(response.read())

    # Check if the file was saved successfully
    if os.path.exists(file_path):
        return True
    else:
        return False

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