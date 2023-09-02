# Not-Another-Twitter-Bot
Not Another Twitter Bot.




---

# NATBOT

Not-Another-Twitter-BOT (NATBOT) is a simple Python-based Twitter bot built using Flask. It allows for automated tweeting through a dedicated web endpoint.
Uses Twitter V2 and Oauth2 to send a message from a single authorised account.
runs a local webserver on 5000

## Features

- OAuth2 Authorization with Twitter API
- SQLite database integration for token storage
- Web endpoint for posting tweets

## Installation

1. Clone this repository:
```bash
git clone <repository_url>
```

2. Navigate into the directory:
```bash
cd <repository_directory>
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```
_Note: `requirements.txt` should list all the necessary packages, including Flask, requests, requests_oauthlib, and more._

## Configuration

1. Set up your environment variables:
```bash
export CLIENT_ID=your_twitter_client_id
export CLIENT_SECRET=your_twitter_client_secret
export REDIRECT_URI=your_redirect_uri
```

## Usage

### Web Endpoint

1. Start the Flask server:
```bash
python Not-Another-Twitter-BOT.py
```

2. Navigate to `http://localhost:5000/` in your browser to initiate the OAuth2 authorization process.

3. Use the `/sendtweet` endpoint to post tweets:
```bash
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"message":"Your Tweet Message Here"}' \
  http://localhost:5000/sendtweet
```

## Example

For an example of how to automate tweets from a file, refer to `sendtweet.py` included in this repository. This script reads a message from a specified file and posts it to Twitter using NATBOT's web endpoint.

## License

This project is open source and available under the [MIT License](LICENSE).

---
