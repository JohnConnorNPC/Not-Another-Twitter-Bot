filename = "message.txt"  # You can change this to the path of your file

import requests
import json
import os

def escape_text_for_json(text):
    """Escapes text for JSON encoding."""
    return json.dumps(text)

def send_tweet_from_file(filename, api_url="http://localhost:5000/sendtweet"):
    """
    Sends a tweet from a local API by reading the message from a file.
    
    Args:
    - filename (str): Path to the file containing the message.
    - api_url (str): URL endpoint for the API. Default is "http://localhost:5000/sendtweet".
    
    Returns:
    - str: Response text or error message.
    """
    
    # Ensure the filename is not empty or None
    if not filename:
        return "error: Invalid filename."
    
    # Read message from file
    if not os.path.exists(filename):
        return "error: File not found."
    
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            message = file.read().strip()
    except UnicodeDecodeError:
        return "error: File encoding issue."
   

    headers = {"Content-Type": "plain/text"}
    
    try:
        response = requests.post(api_url, headers=headers, data=message)
    except requests.RequestException as e:
        return f"error: Failed to send request. {str(e)}"
    
    # Check for errors in API response
    return response.text

# Call function
result = send_tweet_from_file(filename)
print(result)
