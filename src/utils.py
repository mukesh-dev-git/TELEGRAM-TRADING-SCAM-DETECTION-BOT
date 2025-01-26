import re
import requests
import easyocr
from langid import classify  
from googletrans import Translator
from sentence_transformers import util
from telethon import functions, types

ocr_reader = easyocr.Reader(['en'])


def is_valid_url(url):
    """
    Checks if a URL is valid.
    """
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or IPv4
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or IPv6
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None


def is_valid_wallet(wallet_address):
    """
    Validates a cryptocurrency wallet address using a regex pattern.
    """
    pattern = r'[13][a-km-zA-HJ-NP-Z1-9]{25,34}'  # Matches Bitcoin wallet addresses
    return re.match(pattern, wallet_address) is not None


# OCR Text Extraction using EasyOCR
def extract_text_from_image(image_data):
    """
    Extracts text from an image using EasyOCR.
    """
    try:        
        result = ocr_reader.readtext(image_data)
        extracted_text = ' '.join([item[1] for item in result])  
        return extracted_text
    except Exception as e:
        print(f"Error extracting text from image: {e}")
        return None


def translate_to_english(text, translator=None):
    """
    Translates a given text to English using Google Translate.
    """
    try:
        translator = translator or Translator()
        lang, _ = classify(text)
        if lang != "en":
            translated = translator.translate(text, src=lang, dest="en")
            return translated.text
        return text
    except Exception as e:
        print(f"Error translating text: {e}")
        return text


def calculate_semantic_similarity(text1, text2, model):
    """
    Calculates the semantic similarity between two texts using a transformer model.
    """
    try:
        embedding1 = model.encode(text1, convert_to_tensor=True)
        embedding2 = model.encode(text2, convert_to_tensor=True)
        similarity = util.cos_sim(embedding1, embedding2).item()
        return similarity
    except Exception as e:
        print(f"Error calculating semantic similarity: {e}")
        return 0


def normalize_risk_score(score, min_value=0, max_value=1):
    """
    Normalizes a risk score to a given range.
    """
    try:
        return (score - min_value) / (max_value - min_value)
    except ZeroDivisionError:
        print("Error: Max value cannot be equal to min value.")
        return 0


def check_phishing_url(url, api_endpoint):
    """
    Checks if a URL is phishing using an external API.
    """
    try:
        response = requests.post(api_endpoint, json={"url": url})
        if response.status_code == 200:
            data = response.json()
            return data.get("is_phishing", False)
        return False
    except Exception as e:
        print(f"Error inspecting URL: {e}")
        return False


def check_wallet_address(wallet, api_endpoint):
    """
    Verifies if a wallet address is associated with scams using an external API.
    """
    try:
        response = requests.post(api_endpoint, json={"wallet": wallet})
        if response.status_code == 200:
            data = response.json()
            return data.get("scam", False)
        return False
    except Exception as e:
        print(f"Error verifying wallet: {e}")
        return False


def save_to_csv(data, file_path, headers=None):
    """
    Saves data to a CSV file, adding headers if the file does not exist.
    """
    import os
    import csv

    file_exists = os.path.isfile(file_path)
    try:
        with open(file_path, "a", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            if not file_exists and headers:
                writer.writerow(headers)
            writer.writerows(data)
    except Exception as e:
        print(f"Error saving to CSV: {e}")


def explain_risk_flags(message_text, flags):
    """
    Provides explanations for risk flags detected in a message.
    """
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


def fetch_channels(client, keyword, save_path="channels.csv"):
    """
    Fetches channels related to the keyword and saves them in CSV.
    """
    try:
        result = client(functions.contacts.SearchRequest(q=keyword, limit=50))
        channels = [
            [channel.id, channel.title, channel.username or "N/A", channel.participants_count or "N/A"]
            for channel in result.chats if isinstance(channel, types.Channel)
        ]

        save_to_csv(channels, save_path, headers=["Channel ID", "Channel Name", "Username", "Members"])
        print(f"Fetched and saved {len(channels)} channels for keyword '{keyword}'.")
    except Exception as e:
        print(f"Error fetching channels: {e}")
