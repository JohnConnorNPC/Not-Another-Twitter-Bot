# NATBOT: Simplified Twitter Automation

**NATBOT** stands for "Not-Another-Twitter-Bot". It's a streamlined Twitter bot coded in Python using Flask. The bot taps into the Twitter V2 API and uses OAuth2 for message deliveries from an authenticated account. On your machine, it runs a local web server on port 5000.

## 🌟 Highlights

- Connect your account and send messages using the API.
- Seamless integration with Twitter's V2 API through OAuth2.
- Token rotation with SQLite.
- Designated web endpoint for tweet dispatches.

## 🚀 Getting Started

### Spin Up a Twitter App
- **https://developer.twitter.com/**
- **Craft a New App:** Inside the Developer Portal, head to 'Projects & Apps' and opt for 'Overview'. Next, hit the 'Create App' button.
- **Jot Down App Details:** Assign a name and describe your app's mission.
- **Tweak App Permissions:** Under 'User authentication settings', opt for 'Read and Write', the Type of app is Web App. set up the Callback URL (e.g., http://127.0.0.1:5000/oauth/callback).
- **Fetch API Credentials:** Under 'Keys and Tokens', note your Client ID & Client Secret for API interactions.

### Step 1: Grab the Code
```bash
git clone https://github.com/JohnConnorNPC/Not-Another-Twitter-Bot
```

### Step 2: Dive into the Project Folder
```bash
cd Not-Another-Twitter-Bot
```

### Step 3: Set Up the Essentials
```bash
pip install -r requirements.txt
```
> 📝 Tip: Make sure all dependencies from `requirements.txt` are in place.

## ⚙️ Configuration

Initialize your environment variables:
```bash
export CLIENT_ID=your_twitter_client_id
export CLIENT_SECRET=your_twitter_client_secret
export REDIRECT_URI=http://127.0.0.1:5000
```

## 🖥️ How to Use

### Interact via Web Endpoint

1. Ignite the Flask server:
```bash
python Not-Another-Twitter-BOT.py
```

2. Launch your browser & head to `http://localhost:5000/` to kick off the OAuth2 handshake.

3. For tweet dispatches, employ the `/sendtweet` endpoint:
```bash
curl -X POST -H "Content-Type: plain/text" -d "Hello World!" http://127.0.0.1:5000/sendtweet
```
![image](https://github.com/JohnConnorNPC/Not-Another-Twitter-Bot/assets/128232619/f8e548d1-77d5-4dab-84d4-af59b1ac3c5d)


## 📚 Examples

This repo provides an example of automating tweets using a file. The provided script, sendtweet.py, demonstrates how to read a message from a file and tweet it using NATBOT's API endpoint.

Setup
Prepare your file: Create a file named message.txt and write your tweet message inside. This file will be read by our script. You can change the file name if needed.
API URL: By default, the script sends requests to http://127.0.0.1:5000/sendtweet. If your API endpoint is different, you can modify the api_url parameter accordingly.

```bash
python sendtweet.py
```


## 📜 License

This endeavor is open-sourced under the [MIT License](LICENSE).
