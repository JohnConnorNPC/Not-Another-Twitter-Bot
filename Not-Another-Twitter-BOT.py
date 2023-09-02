import base64
import hashlib
import os
import json
import re
import requests
import sqlite3
from datetime import datetime, timedelta
from flask import Flask, request, redirect, session, g, jsonify
from requests_oauthlib import OAuth2Session

app = Flask(__name__)
app.secret_key = os.urandom(50)

# SQLite setup
DATABASE = 'tokens.db'

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

# Create the oauth_tokens table if it doesn't exist
with app.app_context():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS oauth_tokens (
            id INTEGER PRIMARY KEY,
            access_token TEXT,
            refresh_token TEXT,
            token_type TEXT,
            expiry_timestamp INTEGER
        )
    ''')
    db.commit()

# OAuth setup
client_id = os.environ.get("CLIENT_ID")
client_secret = os.environ.get("CLIENT_SECRET")
auth_url = "https://twitter.com/i/oauth2/authorize"
token_url = "https://api.twitter.com/2/oauth2/token"
redirect_uri = os.environ.get("REDIRECT_URI")
scopes = ["tweet.read", "users.read", "tweet.write", "offline.access"]

code_verifier = base64.urlsafe_b64encode(os.urandom(30)).decode("utf-8")
code_verifier = re.sub("[^a-zA-Z0-9]+", "", code_verifier)

code_challenge = hashlib.sha256(code_verifier.encode("utf-8")).digest()
code_challenge = base64.urlsafe_b64encode(code_challenge).decode("utf-8")
code_challenge = code_challenge.replace("=", "")

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

# Decoding methods
def decode_base64(encoded_message):
    return base64.b64decode(encoded_message).decode()

def decode_hex(encoded_message):
    return bytes.fromhex(encoded_message).decode()

def send_tweet_with_decoded_message(decoded_message, db, cursor):
    if not decoded_message:
        return jsonify({"error": "Message not provided"}), 400

    cursor.execute("SELECT access_token, refresh_token, token_type, expiry_timestamp FROM oauth_tokens LIMIT 1")
    data = cursor.fetchone()
    if not data:
        return jsonify({"error": "No token found. Please authorize the app first."}), 400

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
            cursor.execute("DELETE FROM oauth_tokens")
            cursor.execute("INSERT INTO oauth_tokens (access_token, refresh_token, token_type, expiry_timestamp) VALUES (?, ?, ?, ?)", 
                    (refreshed_token['access_token'], refreshed_token['refresh_token'], refreshed_token['token_type'], token_expiry_timestamp))
            db.commit()
            token = refreshed_token
        except Exception as e:
            return jsonify({"error": "Failed to refresh token. Reauthorization might be needed.", "details": str(e)}), 500

    response = post_tweet(decoded_message, token)
    if response.status_code != 201:
        try:
            twitter = make_token()
            refreshed_token = twitter.refresh_token(
                client_id=client_id,
                client_secret=client_secret,
                token_url=token_url,
                refresh_token=token['refresh_token'],
            )
            token_expiry_timestamp = (datetime.now() + timedelta(seconds=refreshed_token['expires_in'])).timestamp()
            cursor.execute("DELETE FROM oauth_tokens")
            cursor.execute("INSERT INTO oauth_tokens (access_token, refresh_token, token_type, expiry_timestamp) VALUES (?, ?, ?, ?)", 
                    (refreshed_token['access_token'], refreshed_token['refresh_token'], refreshed_token['token_type'], token_expiry_timestamp))
            db.commit()
            response = post_tweet(decoded_message, refreshed_token)
            if response.status_code == 201:
                return jsonify({"success": True, "message": "Tweet sent successfully after refreshing token!"})
            else:
                return jsonify({"error": "Failed to send tweet even after refreshing token.", "details": response.json()}), 500
        except Exception as e:
            return jsonify({"error": "Failed to send tweet and token refresh also failed.", "details": str(e)}), 500
    else:
        return jsonify({"success": True, "message": "Tweet sent successfully!"})

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
    cursor.execute("DELETE FROM oauth_tokens")
    cursor.execute("INSERT INTO oauth_tokens (access_token, refresh_token, token_type, expiry_timestamp) VALUES (?, ?, ?, ?)", 
                   (token['access_token'], token['refresh_token'], token['token_type'], token_expiry_timestamp))
    db.commit()
    return "Token stored successfully!"

@app.route('/sendtweet', methods=['POST'])
def send_tweet_endpoint_plain():
    print(request.data)  # Log received data
    message = request.data.decode('utf-8')

    db = get_db()
    cursor = db.cursor()
    return send_tweet_with_decoded_message(message, db, cursor)

@app.route('/sendtweet_base64', methods=['POST'])
def send_tweet_endpoint_base64():
    print(request.data)  # Log received data
    encoded_message = request.json.get('message')
    
    if not encoded_message:
        return jsonify({"error": "Message not provided"}), 400

    decoded_message = decode_base64(encoded_message)

    db = get_db()
    cursor = db.cursor()
    return send_tweet_with_decoded_message(decoded_message, db, cursor)

@app.route('/sendtweet_hex', methods=['POST'])
def send_tweet_endpoint_hex():
    print(request.data)  # Log received data
    encoded_message = request.json.get('message')
    
    if not encoded_message:
        return jsonify({"error": "Message not provided"}), 400

    decoded_message = decode_hex(encoded_message)

    db = get_db()
    cursor = db.cursor()
    return send_tweet_with_decoded_message(decoded_message, db, cursor)

if __name__ == "__main__":
    app.run()

