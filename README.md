# telegram-movie-bot
# 🎬 Telegram Movie Bot

A Telegram bot to upload movies to a channel and save details in MongoDB Atlas.  
Supports multi-quality search and direct download via Telegram.

## 🚀 Deploy on Render

1. Fork or clone this repo.
2. Push to your GitHub account.
3. On [Render.com](https://render.com):
   - New + → Web Service
   - Connect GitHub repo
   - Environment:
     - BOT_TOKEN = `your telegram bot token`
     - MONGO_URI = `your MongoDB Atlas URI`
     - CHANNEL_ID = `-100xxxxxxxxx` (channel numeric ID)
   - Start Command:
     ```
     python bot.py
     ```

4. Deploy and enjoy 🎉

## 🔧 Commands
- `/search <movie name>` → Search movies by title.
