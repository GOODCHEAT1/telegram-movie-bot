
import telebot
from pymongo import MongoClient
import os

# ---------------- CONFIG ----------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
MONGO_URI = os.getenv("MONGO_URI")

# ----------------------------------------
bot = telebot.TeleBot(BOT_TOKEN)
client = MongoClient(MONGO_URI)
db = client["movie_db"]
movies = db["movies"]

# -------- Upload Handler --------
@bot.message_handler(content_types=['video'])
def handle_video(message):
    try:
        file_id = message.video.file_id
        title_quality = message.caption or "Untitled Movie"

        if "|" in title_quality:
            title, quality = [x.strip() for x in title_quality.split("|", 1)]
        else:
            title, quality = title_quality, "unknown"

        thumb = message.video.thumb.file_id if message.video.thumb else None
        size = message.video.file_size
        duration = message.video.duration

        # Forward video to channel
        sent = bot.send_video(
            chat_id=CHANNEL_ID,
            video=file_id,
            caption=f"{title} ({quality})",
            supports_streaming=True
        )

        # Save in DB
        movie_data = {
            "title": title.lower(),
            "quality": quality.lower(),
            "file_id": file_id,
            "channel_message_id": sent.message_id,
            "channel_id": CHANNEL_ID,
            "thumb_id": thumb,
            "size": size,
            "duration": duration,
            "uploader_id": message.from_user.id,
            "uploader_name": f"{message.from_user.first_name} {message.from_user.last_name or ''}"
        }
        movies.insert_one(movie_data)

        bot.reply_to(message, f"✅ Saved & uploaded!\n\n🎬 {title} ({quality})")

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")


# -------- Search Command --------
@bot.message_handler(commands=['search'])
def search_movie(message):
    query = message.text.replace("/search", "").strip().lower()
    if not query:
        bot.reply_to(message, "Usage: `/search movie name`", parse_mode="Markdown")
        return

    results = list(movies.find({"title": {"$regex": query, "$options": "i"}}))
    if not results:
        bot.reply_to(message, "❌ No movies found.")
        return

    grouped = {}
    for movie in results:
        q = movie["quality"]
        grouped[q] = movie

    from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
    markup = InlineKeyboardMarkup()
    for quality, movie in grouped.items():
        markup.add(InlineKeyboardButton(
            text=f"{quality.upper()}",
            callback_data=f"get_{movie['file_id']}"
        ))

    bot.send_message(
        chat_id=message.chat.id,
        text=f"🎬 Found {results[0]['title'].title()} — Select Quality:",
        reply_markup=markup
    )


# -------- Callback Handler --------
@bot.callback_query_handler(func=lambda call: call.data.startswith("get_"))
def send_movie(call):
    file_id = call.data.replace("get_", "")
    movie = movies.find_one({"file_id": file_id})
    if not movie:
        bot.answer_callback_query(call.id, "Movie not found ❌")
        return

    bot.send_video(
        chat_id=call.message.chat.id,
        video=movie["file_id"],
        caption=f"🎬 {movie['title'].title()} ({movie['quality'].upper()})",
        supports_streaming=True
    )
    bot.answer_callback_query(call.id, "🎥 Sending...")


# -------- Run Bot Function --------
def run_bot():
    print("🤖 Bot started with multi-quality support...")
    bot.infinity_polling()
