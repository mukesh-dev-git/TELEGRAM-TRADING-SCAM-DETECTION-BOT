import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
import json
import csv
import asyncio
from telethon import TelegramClient, events, functions, types
from telethon.errors.rpcerrorlist import ChatAdminRequiredError
from scam_detection import analyze_message, save_to_csv, send_real_time_alert

# Load configuration
with open("config.json", "r") as config_file:
    config = json.load(config_file)

API_ID = config["telegram_api"]["api_id"]
API_HASH = config["telegram_api"]["api_hash"]
ADMIN_CHAT_ID = config["telegram_api"]["admin_chat_id"]
TARGET_CHANNELS = config["target_channels"]
CHANNELS_CSV_PATH = "channels.csv"

client = TelegramClient("crypto_scanner", API_ID, API_HASH)

async def fetch_channels_by_keyword(keyword):
    try:
        result = await client(functions.contacts.SearchRequest(
            q=keyword,
            limit=50
        ))
        channels_data = []
        for chat in result.chats:
            from telethon.tl.types import Channel

            if isinstance(chat, Channel): 
                channels_data.append([
                    chat.id,
                    chat.title,
                    chat.username or "N/A",
                    chat.participants_count or "N/A",
                ])
                TARGET_CHANNELS.append(chat.id)

        save_to_csv(channels_data, "channels.csv", headers=["Channel ID", "Name", "Username", "Members"])
        print(f"Fetched and saved {len(channels_data)} channels related to {keyword}.")
    except Exception as e:
        print(f"Error fetching channels by keyword: {e}")

from datetime import datetime

async def fetch_last_messages(channel_id):
    """
    Fetch the last 100 messages from a channel and analyze them.
    """
    try:
        channel_entity = await client.get_entity(channel_id)
        channel_name = channel_entity.title

        messages = await client(functions.messages.GetHistoryRequest(
            peer=channel_id,
            offset_id=0,
            offset_date=None,
            add_offset=0,
            limit=100,
            max_id=0,
            min_id=0,
            hash=0
        ))

        for message in messages.messages:
            if hasattr(message, "message") and message.message:
                risk_score, flags, explanations = analyze_message(message.message)
                if risk_score > 0:

                    save_to_csv([[channel_name, message.message, risk_score, flags, explanations]])
                   
                    send_real_time_alert(channel_name, message.message, risk_score, flags)
    except ChatAdminRequiredError:
        print(f"Cannot fetch messages from channel {channel_id}: Admin rights required.")
    except Exception as e:
        print(f"Error fetching messages from channel {channel_id}: {e}")

@client.on(events.NewMessage(chats=TARGET_CHANNELS))
async def monitor_new_messages(event):
    """
    Real-time monitoring of new messages in target channels.
    """
    try:
        message = event.message
        if message and hasattr(message, "message") and message.message:
            print(f"New message in {event.chat.title}: {message.message}")
                        
            risk_score, flags, explanations = analyze_message(message.message)
            if risk_score > 0:
               
                save_to_csv([[event.chat.title, message.message, risk_score, flags, explanations]])
               
                send_real_time_alert(event.chat.title, message.message, risk_score, flags)
    except Exception as e:
        print(f"Error processing new message: {e}")

async def main():
    print("Starting Telegram Scam Detection Bot...")
    await client.start()
  
    print("You can add new channel IDs for the bot to monitor.")
    add_target_channels()

    keywords = ["crypto", "bitcoin"]
    for keyword in keywords:
        await fetch_channels_by_keyword(keyword)
   
    for channel_id in TARGET_CHANNELS:
        await fetch_last_messages(channel_id)

    print("Bot is now running in real-time mode.")
    await client.run_until_disconnected()

def add_target_channels():
    """
    Allows the user to add channel IDs dynamically during bot startup.
    """
    try:
        while True:
            new_channel_id = input("Enter a new channel ID to monitor (or type 'done' to finish): ")
            if new_channel_id.lower() == "done":
                break
            if not new_channel_id.startswith("-100"):
                print("Channel ID must start with '-100'. Please try again.")
                continue
            try:
                TARGET_CHANNELS.append(int(new_channel_id))
                print(f"Channel ID {new_channel_id} added successfully!")
            except ValueError:
                print("Invalid input. Please enter a valid numeric channel ID.")
    except KeyboardInterrupt:
        print("\nExiting channel addition process...")

if __name__ == "__main__":
    asyncio.run(main())
