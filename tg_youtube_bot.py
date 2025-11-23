import os
import tempfile

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from youtube_uploader import upload_video
from llm_helper import generate_youtube_assets

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OWNER_ID = os.getenv("TELEGRAM_OWNER_ID")  # optional restriction


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if OWNER_ID and str(chat_id) != str(OWNER_ID):
        await update.message.reply_text("This bot is private.")
        return
    await update.message.reply_text(
        "Send me a video (as a video, not as a file), with a short caption.\n"
        "I'll auto-generate a YouTube Short title/description/tags and upload it to your channel."
    )


async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if OWNER_ID and str(chat_id) != str(OWNER_ID):
        await update.message.reply_text("This bot is private.")
        return

    message = update.effective_message
    if not message.video:
        await update.message.reply_text("Please send a video (not just a file).")
        return

    caption = message.caption or ""
    await update.message.reply_text("Received video. Downloading and preparing upload...")

    # 1. Download video to a temp file
    video = message.video
    file = await context.bot.get_file(video.file_id)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
        temp_path = tmp.name
        await file.download_to_drive(custom_path=temp_path)

    # 2. Use caption to generate metadata (or fallback)
    # We'll treat caption as "topic" and use generic person/niche
    celeb = "a trending public figure"
    niche = "general viral content"
    style = "Commentary"
    region = "Global"
    chosen_topic = caption if caption else "Viral short about a current hot topic"

    try:
        assets = generate_youtube_assets(celeb, niche, style, region, chosen_topic)
        # pick first title
        title = assets["titles"][0] if assets["titles"] else chosen_topic
        description = assets["description"]
        tags = assets["tags"]
    except Exception as e:
        # Fallback: use caption directly
        title = caption if caption else "Untitled Short"
        description = caption
        tags = []

    await update.message.reply_text(
        f"Uploading to YouTube...\n\nTitle: {title}\n\nThis may take a while..."
    )

    # 3. Upload to YouTube
    try:
        youtube_url = upload_video(
            video_file=temp_path,
            title=title,
            description=description,
            tags=tags,
            privacy_status="unlisted",  # change to 'public' if you want
        )
    except Exception as e:
        await update.message.reply_text(f"Error uploading to YouTube: {e}")
        # Clean up temp
        try:
            os.remove(temp_path)
        except OSError:
            pass
        return

    # Clean up local temp file
    try:
        os.remove(temp_path)
    except OSError:
        pass

    # 4. Reply with YouTube link
    await update.message.reply_text(
        f"Upload complete!\n\nYouTube link:\n{youtube_url}"
    )


def main():
    if not BOT_TOKEN:
        print("TELEGRAM_BOT_TOKEN not set in .env")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VIDEO & ~filters.COMMAND, handle_video))

    print("Telegram YouTube bot running. Press Ctrl+C to stop.")
    app.run_polling()


if __name__ == "__main__":
    main()