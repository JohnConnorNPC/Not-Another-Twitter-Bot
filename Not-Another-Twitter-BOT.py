import base64
import hashlib
import os
import re
import sys
import requests
import sqlite3
from datetime import datetime, timedelta
from flask import Flask, request, redirect, session, g, jsonify
from requests_oauthlib import OAuth2Session

# Constants
DATABASE = os.environ.get('DATABASE_NAME', 'tokens.db')
client_id = os.environ.get("CLIENT_ID")
client_secret = os.environ.get("CLIENT_SECRET")
redirect_uri = os.environ.get("REDIRECT_URI", "http://127.0.0.1:5000/oauth/callback")
auth_url = "https://twitter.com/i/oauth2/authorize"
token_url = "https://api.twitter.com/2/oauth2/token"
scopes = ["tweet.read", "users.read", "tweet.write", "offline.access"]

# SQL Queries
CREATE_TABLE_QUERY = '''
    CREATE TABLE IF NOT EXISTS oauth_tokens (
        id INTEGER PRIMARY KEY,
        access_token TEXT,
        refresh_token TEXT,
        token_type TEXT,
        expiry_timestamp INTEGER
    )
'''
SELECT_TOKEN_QUERY = "SELECT access_token, refresh_token, token_type, expiry_timestamp FROM oauth_tokens LIMIT 1"
DELETE_TOKENS_QUERY = "DELETE FROM oauth_tokens"
INSERT_TOKEN_QUERY = "INSERT INTO oauth_tokens (access_token, refresh_token, token_type, expiry_timestamp) VALUES (?, ?, ?, ?)"


# Initialization
app = Flask(__name__)
app.secret_key = os.urandom(50)

# Extract the IP and port using regex
match = re.search(r'http://([\d\.]+):(\d+)', redirect_uri)
if match:
    host = match.group(1)
    port = int(match.group(2))
else:
    print("Invalid REDIRECT_URI format.")
    sys.exit(1)

# Validate IP
ip_pattern = r'^(25[0-5]|2[0-4][0-9]|[0-1]?[0-9]{1,2})(\.(25[0-5]|2[0-4][0-9]|[0-1]?[0-9]{1,2})){3}$'
if not re.match(ip_pattern, host):
    host = "0.0.0.0"

if not (1025 <= port <= 65535):
    print("Invalid port number in REDIRECT_URI. Port must be between 1025 and 65535.")
    sys.exit(1)

# Code verifier and challenge for OAuth2 PKCE
code_verifier = base64.urlsafe_b64encode(os.urandom(30)).decode("utf-8")
code_verifier = re.sub("[^a-zA-Z0-9]+", "", code_verifier)
code_challenge = hashlib.sha256(code_verifier.encode("utf-8")).digest()
code_challenge = base64.urlsafe_b64encode(code_challenge).decode("utf-8")
code_challenge = code_challenge.replace("=", "")

# SQLite setup
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

with app.app_context():
    db = get_db()
    cursor = db.cursor()
    cursor.execute(CREATE_TABLE_QUERY)
    db.commit()

# OAuth setup
def make_token():
    return OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scopes)

def post_tweet(message, token):
    payload = {"text": message}
    return requests.request(
        "POST",
        "https://api.twitter.com/2/tweets",
        json=payload,
        headers={
            "Authorization": "Bearer {}".format(token["access_token"]),
            "Content-Type": "application/json",
        },
    )

def delete_tweet(tweet_id, token):
    headers = {
        "Authorization": "Bearer {}".format(token["access_token"]),
        "Content-Type": "application/json",
    }
    response = requests.request("DELETE", f"https://api.twitter.com/2/tweets/{tweet_id}", headers=headers)
    return response

def get_or_refresh_token():
    db = get_db()
    cursor = db.cursor()
    cursor.execute(SELECT_TOKEN_QUERY)
    data = cursor.fetchone()
    if not data:
        return None, {"error": "No token found. Please authorize the app first."}, 400

    token = {
        'access_token': data[0],
        'refresh_token': data[1],
        'token_type': data[2],
        'expiry_timestamp': data[3]
    }

    if datetime.now() >= datetime.fromtimestamp(token['expiry_timestamp']):
        try:
            twitter = make_token()
            refreshed_token = twitter.refresh_token(
                client_id=client_id,
                client_secret=client_secret,
                token_url=token_url,
                refresh_token=token['refresh_token'],
            )
            token_expiry_timestamp = (datetime.now() + timedelta(seconds=refreshed_token['expires_in'])).timestamp()
            cursor.execute(DELETE_TOKENS_QUERY)
            cursor.execute(INSERT_TOKEN_QUERY, 
                    (refreshed_token['access_token'], refreshed_token['refresh_token'], refreshed_token['token_type'], token_expiry_timestamp))
            db.commit()
            return refreshed_token, None, None
        except Exception as e:
            return None, {"error": "Failed to refresh token. Reauthorization might be needed.", "details": str(e)}, 500
    
    return token, None, None

@app.route("/")
def demo():
    twitter = make_token()
    authorization_url, state = twitter.authorization_url(
        auth_url, code_challenge=code_challenge, code_challenge_method="S256"
    )
    session["oauth_state"] = state
    return redirect(authorization_url)

@app.route("/oauth/callback", methods=["GET"])
def callback():
    twitter = make_token()
    code = request.args.get("code")
    token = twitter.fetch_token(
        token_url=token_url,
        client_secret=client_secret,
        code_verifier=code_verifier,
        code=code,
    )
    token_expiry_timestamp = (datetime.now() + timedelta(seconds=token['expires_in'])).timestamp()
    db = get_db()
    cursor = db.cursor()
    cursor.execute(DELETE_TOKENS_QUERY)
    cursor.execute(INSERT_TOKEN_QUERY, 
                   (token['access_token'], token['refresh_token'], token['token_type'], token_expiry_timestamp))
    db.commit()
    return "Token stored successfully!"

@app.route('/sendtweet', methods=['POST'])
def send_tweet_endpoint_plain():
    print(request.data)  # Log received data
    message = request.data.decode('utf-8')

    token, error, status_code = get_or_refresh_token()
    if error:
        return jsonify(error), status_code

    response = post_tweet(message, token)
    if response.status_code == 201:
        return jsonify({"success": True, "message": "Tweet sent successfully!" , "response" : response.json()})
    else:
        return jsonify({"error": "Failed to send tweet.", "details": response.json()}), 500

@app.route('/deletetweet/<tweet_id>', methods=['DELETE'])
def delete_tweet_endpoint(tweet_id):
    token, error, status_code = get_or_refresh_token()
    if error:
        return jsonify(error), status_code

    response = delete_tweet(tweet_id, token)
    if response.status_code == 200:
        return jsonify({"success": True, "message": "Tweet deleted successfully!"})
    else:
        return jsonify({"error": "Failed to delete tweet.", "details": response.json()}), 500

if __name__ == "__main__":
    app.run(host=host, port=port)
