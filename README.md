# Telegram Scam Detection Bot

## Overview
The Telegram Scam Detection Bot is a powerful Python-based tool designed to monitor and analyze messages in Telegram channels for potential scams. It uses natural language processing (NLP), sentiment analysis, keyword matching, and external APIs to detect and flag scam-related content in real-time.

---

## Features

1. **Real-Time Scam Detection**:
   - Monitors Telegram channels and flags suspicious messages.
   - Alerts the admin in real-time about flagged content.

2. **Multi-Modal Analysis**:
   - Analyzes text messages, URLs, and wallet addresses.
   - Extracts and analyzes text from images (using OCR).

3. **Explainable AI**:
   - Provides detailed explanations for why messages were flagged.

4. **Flexible Configuration**:
   - Add or remove target channels dynamically.
   - Adjustable risk thresholds and keyword matching.

5. **Data Logging**:
   - Logs flagged messages to a CSV file for auditing and review.

---

## Prerequisites

### Python Requirements
- **Python**: Version **3.10.x** to **3.12.x** (3.13 is not supported).

### Telegram API Credentials
- Obtain your **API ID** and **API Hash** from [Telegram's Developer Portal](https://my.telegram.org/).

---

## Installation Guide

### Step 1: Download or Clone the Repository
Download or clone this repository to your local machine:
```bash
https://github.com/yourusername/telegram-scam-detection-bot.git
```

### Step 2: Navigate to the Project Directory
Open a terminal and navigate to the project folder:
```bash
cd path/to/telegram-scam-detection-bot
```

### Step 3: Run the Setup Script
Run the setup script to ensure Python compatibility and install all dependencies:
```bash
python setup.py
```
This script will:
- Check your Python version.
- Install `pip` if missing.
- Install all required libraries from `requirements.txt`.

### Step 4: Configure the Bot
Edit the `config.json` file in the project directory:
1. Add your Telegram **API ID** and **API Hash**.
2. Set the **admin chat ID** to receive alerts.
3. Add any initial target channels (optional).

Example `config.json`:
```json
{
  "telegram_api": {
    "api_id": 123456,
    "api_hash": "your_api_hash",
    "admin_chat_id": 987654321
  },
  "target_channels": [
    -1001234567890
  ],
  "settings": {
    "csv_file_path": "flagged_messages.csv"
  }
}
```

---

## Usage

### Step 1: Activate the Virtual Environment
If a virtual environment was created:
- **Windows**:
  ```bash
  venv\Scripts\activate
  ```
- **macOS/Linux**:
  ```bash
  source venv/bin/activate
  ```

### Step 2: Start the Bot
Run the main script:
```bash
python src/main.py
```

### Step 3: Add Target Channels Dynamically
When prompted, you can add new Telegram channel IDs for the bot to monitor. Type `done` when finished.

---

## Deployment (Optional)
For continuous operation, consider deploying the bot on a server or cloud platform.

### Example: Running on a VPS
1. Install Python and Git on your server.
2. Clone the repository and follow the setup steps.
3. Use a process manager like **`pm2`** or **`supervisor`** to keep the bot running.

---

## Troubleshooting

### Common Issues
1. **Python Version Error**:
   - Ensure Python is between versions **3.10** and **3.12**.
   - Download the correct version from [python.org](https://www.python.org/).

2. **Permission Issues**:
   - On Windows, run the terminal or Command Prompt as **Administrator**.

3. **Missing Dependencies**:
   - Reinstall libraries:
     ```bash
     pip install -r requirements.txt
     ```

4. **Hugging Face Symlink Warning**:
   - Enable Developer Mode in Windows or run Python as Administrator.

---

## License
This project is licensed under the MIT License.

---

## Contact
For any issues or questions, contact:
- **Email**: your_email@example.com
- **GitHub**: [yourusername](https://github.com/yourusername)

---

Happy Monitoring!

