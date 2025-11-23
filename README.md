# YouTube Shorts Tool

A local web app + Telegram bot to:

- Auto-pick trending public figures (celebrities / public figures) by niche & region
- Generate viral YouTube Shorts titles, descriptions, and tags
- Let you select a title and upload your video to YouTube with that metadata
- Optionally send the same video + caption via a Telegram bot

## Features

- **Web app (Flask)**
  - Auto / manual celebrity selection
  - Topic ideas
  - 10+ title ideas
  - Description + tags
  - Upload page to upload a video file and send to YouTube

- **YouTube integration**
  - Uses YouTube Data API v3 (OAuth)
  - Uploads as `unlisted` by default (configurable)

- **Telegram bot**
  - Send a video directly from your phone to Telegram
  - Bot generates metadata and uploads to YouTube
  - Replies with the YouTube link

## Setup

1. Clone the repo:

```bash
git clone https://github.com/vincevision/youtube-shorts-tool.git
cd youtube-shorts-tool
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt  # or manually install dependencies
