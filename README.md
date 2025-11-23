
# YouTube Shorts Tool

A local web app + Telegram bot to:

- Auto-pick trending public figures in a chosen niche/region (via Groq / Llama 3)
- Generate viral YouTube Shorts **titles, descriptions, and tags**
- Let you select a title and upload your video to **YouTube** with that metadata
- (Optional) Upload a Short directly from **Telegram** (send a video to the bot, it uploads to YouTube and replies with the link)

This is meant for **personal / educational** use and runs on your machine.

---

## Features

### Web App (Flask)

- Auto or manual **celebrity/public figure** selection
- Topic ideas about that person
- 10 title ideas per topic
- 1 description with hashtags
- 20 SEO-friendly tags
- “Next: Upload” page:
  - Select your final Short video (`.mp4` or other video)
  - Upload to your YouTube channel via YouTube Data API

### YouTube Integration

- Uses **YouTube Data API v3** (OAuth Desktop client)
- First time: browser opens, you grant permission to your account
- Then uploads are authenticated via saved `token.json`
- Uploads as `unlisted` by default (configurable in code)

### Telegram Bot

- `tg_youtube_bot.py`:
  - Send a **video** to the bot in Telegram (with caption)
  - Bot downloads it on your machine
  - Generates title/description/tags
  - Uploads to YouTube
  - Replies with the YouTube link

---

## Project Structure

Typical layout:

```text
youtube-shorts-tool/
  app.py                 # Flask web app
  llm_helper.py          # Groq/Llama calls (people/topics/assets)
  youtube_uploader.py    # YouTube Data API upload helper
  tg_youtube_bot.py      # Telegram -> YouTube upload bot
  templates/
    index.html
    topics.html
    result.html
    upload.html
  uploads/               # local uploads (created at runtime)
  .env                   # local secrets (NOT in Git)
  credentials.json       # YouTube OAuth client (NOT in Git)
  token.json             # YouTube OAuth token (NOT in Git)
  venv/                  # Python virtualenv (NOT in Git)
  requirements.txt
  README.md
```

---

## Prerequisites

You’ll need:

- A **Groq API key** (for Llama 3)
- A **Telegram bot token**
- A **YouTube OAuth client** (`credentials.json`) from Google Cloud Console

Details for each are below.

---

## Install & Run – Windows

### 1. Install Python and Git

- Install Python 3.x from https://python.org
  - Ensure “Add Python to PATH” is selected.
- Install Git from https://git-scm.com/download/win
  - Choose “Git from the command line” option.

Verify in Command Prompt:

```cmd
python --version
git --version
```

### 2. Clone the repo

```cmd
cd %USERPROFILE%\Desktop
git clone https://github.com/vincevision/youtube-shorts-tool.git
cd youtube-shorts-tool
```

(Replace URL with your repo if different.)

### 3. Create virtualenv and install requirements

```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Create `.env`

In the project folder:

```cmd
notepad .env
```

Paste:

```env
FLASK_SECRET_KEY=some_random_secret_here
GROQ_API_KEY=your_groq_api_key_here

TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_OWNER_ID=your_telegram_numeric_user_id_here  # optional but recommended
```

- `GROQ_API_KEY`: from https://console.groq.com
- `TELEGRAM_BOT_TOKEN`: from BotFather on Telegram
- `TELEGRAM_OWNER_ID`: your Telegram numeric ID (see below how to get it)

Save file.

### 5. Get YouTube `credentials.json` (Desktop OAuth)

1. Go to Google Cloud Console:  
   https://console.cloud.google.com/

2. Create/select a project.

3. Enable **YouTube Data API v3**:
   - Left menu → APIs & Services → Library
   - Search for “YouTube Data API v3”
   - Click **Enable**

4. Configure OAuth consent screen:
   - Left menu → **OAuth consent screen**
   - User type: **External**
   - App name: e.g. “Shorts Uploader”
   - Fill required fields (support email, developer email)
   - Save

5. Create OAuth client:
   - Left menu → **Credentials**
   - **Create Credentials → OAuth client ID**
   - Application type: **Desktop app**
   - Name: `Desktop YouTube Uploader`
   - Create, then **Download JSON**

6. Rename downloaded file to:

   ```text
   credentials.json
   ```

7. Move `credentials.json` into your project folder (`youtube-shorts-tool`):

   ```text
   youtube-shorts-tool/
     app.py
     llm_helper.py
     youtube_uploader.py
     credentials.json   <-- here
     ...
   ```

First time you upload on this machine, the app will open a browser window asking you to log in and approve.

---

## Install & Run – Linux (Ubuntu/Debian example)

### 1. Install Python, venv, and Git

```bash
sudo apt update
sudo apt install -y python3 python3-venv git
```

Verify:

```bash
python3 --version
git --version
```

### 2. Clone the repo

```bash
mkdir -p ~/projects
cd ~/projects

git clone https://github.com/vincevision/youtube-shorts-tool.git
cd youtube-shorts-tool
```

### 3. Create virtualenv and install requirements

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Create `.env`

```bash
nano .env
```

Paste:

```env
FLASK_SECRET_KEY=some_random_secret_here
GROQ_API_KEY=your_groq_api_key_here

TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_OWNER_ID=your_telegram_numeric_user_id_here
```

Save (`Ctrl+O`, Enter, `Ctrl+X`).

### 5. Add `credentials.json` for YouTube

Copy `credentials.json` from your Windows machine (or create it anew as described above) into:

```text
~/projects/youtube-shorts-tool/credentials.json
```

So the file sits next to `app.py`.

---

## Install & Run – Termux (Android)

Termux is more limited but you can get this working locally on Android.

### 1. Install Termux and basic packages

- Install **Termux** from F-Droid (recommended) or trusted source.
- In Termux:

```bash
pkg update
pkg upgrade
pkg install python git
```

### 2. Clone the repo

```bash
cd ~
git clone https://github.com/vincevision/youtube-shorts-tool.git
cd youtube-shorts-tool
```

### 3. (Optional) Create virtualenv

Sometimes `venv` works in Termux, sometimes not; if it fails, you can install globally.

Try:

```bash
python -m venv venv
source venv/bin/activate
```

If `venv` fails, skip it and just:

```bash
pip install -r requirements.txt
```

### 4. Create `.env`

```bash
nano .env
```

Same content:

```env
FLASK_SECRET_KEY=some_random_secret_here
GROQ_API_KEY=your_groq_api_key_here

TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_OWNER_ID=your_telegram_numeric_user_id_here
```

### 5. Put `credentials.json` in Termux

You need to place `credentials.json` in the project folder:

```text
~/youtube-shorts-tool/credentials.json
```

You can:

- Copy it via `termux-setup-storage` and move from `/sdcard` to your project, or
- Use a cloud storage + `wget`/`curl` to fetch it.

Keep in mind: OAuth popup in Termux is trickier (no browser by default). You might prefer to do YouTube uploads from a desktop/laptop and use Termux only for the **Telegram bot** side.

---

## Getting Your Telegram User ID (`TELEGRAM_OWNER_ID`)

Optional but recommended so only you can use the bot.

You can use a helper script like:

```python
# get_chat_id.py (one-time helper)
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"Your chat ID is: {chat_id}")
    print("Chat ID:", chat_id)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == "__main__":
    main()
```

Run it:

```bash
python get_chat_id.py
```

In Telegram:

- Talk to your bot.
- Send `/start`.
- It replies with your chat ID and prints it in the console.  
  Use that number as `TELEGRAM_OWNER_ID`.

---

## Running the Web App

### On Windows

```cmd
cd "C:\Users\YOURNAME\path\to\youtube-shorts-tool"
venv\Scripts\activate
python app.py
```

Then open in browser (on that machine):

- `http://127.0.0.1:5000/`

### On Linux

```bash
cd ~/projects/youtube-shorts-tool
source venv/bin/activate
python3 app.py
```

Browser:

- `http://127.0.0.1:5000/`

### Web App Flow

1. Open `/`:
   - Fill in:
     - Celebrity/public figure (or leave blank)
     - Niche (e.g. “football”, “Kenyan politics”)
     - Style (Commentary, Reaction, etc.)
     - Region (Global, Kenya, US, etc.)
   - Optionally tick **Auto-pick person & topic**.

2. Click **Generate ideas**:
   - Manual mode: choose a topic from the list.
   - Auto mode: jumps straight to results.

3. On **result** page:
   - Click a title to select it.
   - Use copy buttons if you want.
   - Click **“Next: Upload video to YouTube”**.

4. On **upload** page:
   - Confirm title/description/tags.
   - Choose your **Short video** file.
   - (Optional) tick “Also send this video and caption to my Telegram bot chat” if you’ve wired that in.
   - Click **Upload**.

5. First upload on a machine:
   - Browser opens, ask you to log into Google and allow YouTube uploads.
   - After allowing, Flask continues and shows the YouTube link.

---

## Running the Telegram Bot

### On Windows

```cmd
cd "C:\Users\YOURNAME\path\to\youtube-shorts-tool"
venv\Scripts\activate
python tg_youtube_bot.py
```

### On Linux

```bash
cd ~/projects/youtube-shorts-tool
source venv/bin/activate
python3 tg_youtube_bot.py
```

### Bot Flow

1. In Telegram, open chat with your bot (the one from BotFather).
2. Send `/start`.
3. Send a **video** (as a video, not as a file) with a short caption.
4. The bot will:
   - Download the video to the machine.
   - Auto-generate title/description/tags using `llm_helper.generate_youtube_assets`.
   - Upload the video to YouTube (using the same `credentials.json`).
   - Reply with the YouTube link.

Note:

- Bot will usually be restricted to the `TELEGRAM_OWNER_ID` you set.
- Make sure `.env` and `credentials.json` exist and are correct, just like for the web app.

---

## Notes & Warnings

- **API keys and credentials**:
  - Never commit `.env`, `credentials.json`, `token.json`, or `venv/` to Git or share them publicly.
- **Quotas**:
  - YouTube and Groq both have API limits. Don’t hammer them with too many calls.
- **Legal / Policy**:
  - Be mindful of platform policies (YouTube, Telegram, Groq).
  - This tool is for your own channels and content; don’t spam.

---

If you follow the above for each platform (Windows, Linux, Termux), you’ll be able to set up and run the app + bot on any machine.
