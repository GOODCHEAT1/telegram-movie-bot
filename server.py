from flask import Flask
import threading
import bot  # yeh bot.py ko import karega

app = Flask(__name__)

@app.route("/")
def home():
    return "🤖 Telegram Movie Bot is running on Render!"

# Flask ke saath bot ko background me start karo
def start_bot():
    bot.run_bot()

threading.Thread(target=start_bot).start()

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
