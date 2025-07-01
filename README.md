# Red_STT_Bot

A Telegram bot for speech recognition from voice and video messages using Nexara (OpenAI Whisper).

## Features

- Accepts voice and video messages in Telegram.
- Recognizes speech using the Nexara STT API (based on OpenAI Whisper).
- Sends the user a text transcription of the audio.
- Logs events via Logfire.
- Can work in groups: automatically recognizes speech from voice and video messages in a group (if given admin rights).

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/BuT9l3b/Red_STT_Bot.git
cd Red_STT_Bot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set environment variables

Create a `.env` file in the project root and add the following:

```
TG_TOKEN=your_telegram_token
NEXARA_TOKEN=your_nexara_token
LOGFIRE_TOKEN=your_logfire_token
```

### 4. Run the bot

```bash
python main.py
```

## Project Structure

- `main.py` — main file to run the Telegram bot.
- `stt.py` — module for working with the Nexara STT API.
- `message_tools.py` — helper functions for sending messages.
- `texts.py` — text templates for messages.

## Usage

1. Start the bot.
2. Send `/start` to it in Telegram.
3. Send a voice or video message.
4. Receive the text transcription of the audio.

## Dependencies

- Python 3.8+
- aiogram
- openai
- httpx
- python-dotenv
- logfire
- telegramify_markdown

Install all dependencies with:

```bash
pip install -r requirements.txt
```

## License

MIT License
