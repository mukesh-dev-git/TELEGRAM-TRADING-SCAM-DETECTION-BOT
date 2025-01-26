import csv
import os
import re
from datetime import datetime
from telethon import TelegramClient, functions, types
from sentence_transformers import SentenceTransformer, util
from transformers import pipeline
from langid import classify  
from rapidfuzz import fuzz  
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
import requests
import easyocr
from googletrans import Translator
import json

try:
    nlp_model = SentenceTransformer("sentence-transformers/paraphrase-MiniLM-L6-v2")  # Updated with the correct model path
except Exception as e:
    print(f"Error loading SentenceTransformer model: {e}")
    nlp_model = None

sentiment_model = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
translator = Translator()

vectorizer = TfidfVectorizer()
ml_classifier = RandomForestClassifier()

SCAM_KEYWORDS = [
    "guaranteed profit", "100% return", "double your money",
    "investment opportunity", "no risk", "get rich quick", "limited time offer",
    "ICO pre-sale", "exclusive tokens", "initial coin offering", "airdrop",
    "pump and dump", "private tip", "inside information", "high leverage",
    "trusted platform", "regulated broker", "withdrawal problems"
]

PHISHING_API = "https://api.phishtank.com/check-url" 
WALLET_VERIFICATION_API = "https://api.scamwallet.com/check"  

import json

with open("config.json", "r") as config_file:
    config = json.load(config_file)

BOT_TOKEN = config.get("TELEGRAM_BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("Bot token not found in config.json. Please ensure it exists.")

TELEGRAM_REPORT_API = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

if __name__ == "__main__":
    print(f"API URL: {TELEGRAM_REPORT_API}")


def extract_text_from_image(image_data):
    try:
        reader = easyocr.Reader(['en'])
        result = reader.readtext(image_data)
        extracted_text = " ".join([text[1] for text in result])
        return extracted_text
    except Exception as e:
        print(f"Error extracting text from image: {e}")
        return None


def translate_to_english(text):
    try:
        lang, _ = classify(text)
        if lang != "en":
            translated = translator.translate(text, src=lang, dest="en")
            return translated.text
        return text
    except Exception as e:
        print(f"Error translating text: {e}")
        return text


def check_wallet_address(wallet):
    try:
        response = requests.post(WALLET_VERIFICATION_API, json={"wallet": wallet})
        if response.status_code == 200:
            data = response.json()
            return data.get("scam", False)
        return False
    except Exception as e:
        print(f"Error verifying wallet: {e}")
        return False


def inspect_url(url):
    try:
        response = requests.post(PHISHING_API, json={"url": url})
        if response.status_code == 200:
            data = response.json()
            return data.get("is_phishing", False)
        return False
    except Exception as e:
        print(f"Error inspecting URL: {e}")
        return False


def is_keyword_match(message_text, keywords, threshold=85):
    for keyword in keywords:
        if fuzz.partial_ratio(message_text.lower(), keyword.lower()) >= threshold:  
            return True
    return False


def detect_language(message):
    try:
        lang, _ = classify(message)
        return lang
    except:
        return "unknown"


def explain_risk_flags(message_text, flags):
    explanations = []
    if "Keyword Match" in flags:
        explanations.append("Message contains keywords commonly used in scams.")
    if "Negative Sentiment" in flags:
        explanations.append("Message has a manipulative or negative tone.")
    if "Semantic Match" in flags:
        explanations.append("Message is semantically similar to known scam phrases.")
    if "Suspicious URL" in flags:
        explanations.append("Message includes potentially phishing URLs.")
    if "Scam Wallet" in flags:
        explanations.append("Message references a suspicious cryptocurrency wallet.")
    return explanations


def analyze_message(message_text):

    lang = detect_language(message_text)
    if lang != "en":
        return None, "Unsupported Language"
   
    urls = re.findall(r'https?://\S+', message_text)
    wallets = re.findall(r'[13][a-km-zA-HJ-NP-Z1-9]{25,34}', message_text)  

    url_flags = any(inspect_url(url) for url in urls)
    wallet_flags = any(check_wallet_address(wallet) for wallet in wallets)
    
    keyword_flag = is_keyword_match(message_text, SCAM_KEYWORDS)
   
    sentiment = sentiment_model(message_text)[0]
    sentiment_flag = sentiment["label"] == "NEGATIVE" and sentiment["score"] > 0.8
   
    suspicious_phrases = [
        "guaranteed profit", "double your money", "investment opportunity",
        "100% return", "no risk", "get rich quick", "limited time offer"
    ]
    similarity_flag = any(
        util.cos_sim(nlp_model.encode(message_text), nlp_model.encode(phrase)).item() > 0.8
        for phrase in suspicious_phrases
    ) if nlp_model else False

    flags = []
    if keyword_flag:
        flags.append("Keyword Match")
    if sentiment_flag:
        flags.append("Negative Sentiment")
    if similarity_flag:
        flags.append("Semantic Match")
    if url_flags:
        flags.append("Suspicious URL")
    if wallet_flags:
        flags.append("Scam Wallet")
   
    scam_risk = (
        (0.3 if keyword_flag else 0) +
        (0.2 if sentiment_flag else 0) +
        (0.2 if similarity_flag else 0) +
        (0.15 if url_flags else 0) +
        (0.15 if wallet_flags else 0)
    )
    
    explanations = explain_risk_flags(message_text, flags)

    return scam_risk, ", ".join(flags), explanations


def save_to_csv(data, file_path="flagged_messages.csv", headers=None):
    """
    Saves data to a CSV file, adding headers if the file does not exist.
    """
    file_exists = os.path.isfile(file_path)
    headers = headers or ["Channel Name", "Message Text", "Risk Score", "Flags", "Explanations"]
    try:
        with open(file_path, "a", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            if not file_exists:
                writer.writerow(headers)
            writer.writerows(data)
    except Exception as e:
        print(f"Error saving to CSV: {e}")


ADMIN_CHAT_ID = "your_admin_chat_id_here"

def send_real_time_alert(channel_name, message_text, risk_score, flags):
    """
    Sends a real-time alert to the admin with details about the flagged message.
    """
    try:
        explanations = explain_risk_flags(message_text, flags.split(", "))
        alert_message = (
            f"🚨 *High-Risk Message Detected* 🚨\n"
            f"Channel: {channel_name}\n"
            f"Message: {message_text}\n"
            f"Risk Score: {risk_score}\n"
            f"Flags: {flags}\n"
            f"Explanation: {', '.join(explanations)}"
        )
                
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)
            ADMIN_CHAT_ID = config.get("ADMIN_CHAT_ID", "your_admin_chat_id_here")

        payload = {
            "chat_id": ADMIN_CHAT_ID,
            "text": alert_message,
            "parse_mode": "Markdown"
        }

        response = requests.post(TELEGRAM_REPORT_API, json=payload)
        if response.status_code == 200:
            print("Real-time alert sent successfully.")
        else:
            print(f"Failed to send alert: {response.json()}")
    except Exception as e:
        print(f"Error sending real-time alert: {e}")


def fetch_channels_and_save(client, keyword, csv_file="channels.csv"):
    """ Fetch public channels by keyword and save metadata to CSV """
    try:
        result = client(functions.contacts.SearchRequest(q=keyword, limit=50))
        channels_data = []

        for channel in result.chats:
            if isinstance(channel, types.Channel):
                channels_data.append([channel.id, channel.title, channel.username or "N/A", channel.participants_count or "N/A"])
       
        save_to_csv(channels_data, csv_file, headers=["ID", "Name", "Username", "Members"])

    except Exception as e:
        print(f"Error fetching channels: {e}")
