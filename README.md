# Not-Another-Twitter-Bot (NATBOT)

Not-Another-Twitter-Bot, or NATBOT, is a straightforward Python-based Twitter bot designed with Flask. It leverages the Twitter V2 API and OAuth2 to send messages from a single authorized account. The bot operates a local web server on port 5000.

## Features

- OAuth2 Authorization with Twitter's V2 API.
- SQLite for secure token storage.
- A dedicated web endpoint for posting tweets.

## Installation

1. Clone this repository:
```bash
git clone https://github.com/JohnConnorNPC/Not-Another-Twitter-Bot
```

2. Navigate into the directory:
```bash
cd Not-Another-Twitter-Bot
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```
_Note: Ensure you have the necessary dependencies listed in `requirements.txt`._

## Configuration

Set up your environment variables:
```bash
export CLIENT_ID=your_twitter_client_id
export CLIENT_SECRET=your_twitter_client_secret
export REDIRECT_URI=http://127.0.0.1:5000
```

## Usage

### Using the Web Endpoint

1. Start the Flask server:
```bash
python Not-Another-Twitter-BOT.py
```

2. Open your browser and navigate to `http://localhost:5000/` to initiate the OAuth2 authorization process.

3. To post tweets, use the `/sendtweet` endpoint:
```bash
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"message":"Your Tweet Message Here"}' \
  http://localhost:5000/sendtweet
```

## Examples

To understand how to automate tweets from a file, refer to the `sendtweet.py` script in this repository. This example demonstrates how to read a message from a specified file and post it to Twitter using NATBOT's web endpoint.

## License

This project is open source and is licensed under the [MIT License](LICENSE).
