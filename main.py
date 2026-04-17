import os, time, threading, random, string
import telebot
import google.generativeai as genai
from flask import Flask

app = Flask(__name__)

# ==========================================
# 🔴 ARYAN'S ULTIMATE BOT CREDENTIALS 🔴
# ==========================================
BOT_TOKEN = "8764748799:AAF_zK7dwMPycJeAY0rY_d6SW79r84wi5P4"
GEMINI_API_KEY = "AIzaSyAui3nTYj1WEvG-Tup-1RQXw3KzHHIhoXQ"
OWNER_ID = 8230119621

# Setup
bot = telebot.TeleBot(BOT_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)

# Safety filters ko 0 kar diya taaki brutal gaali/roast ho sake
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
]
model = genai.GenerativeModel('gemini-1.5-flash', safety_settings=safety_settings)

# ==========================================
# 🧠 AI BRAIN & PERSONA (Jaisi Karni Waisi Bharni)
# ==========================================
SYSTEM_PROMPT = """Tu ek loyal, aggressive aur highly protective 'Human-Bot' hai. 
Tera boss 'Aryan' hai. Aryan details: Age 16, From Jammu & Kashmir, Class 10th, Coder & Developer.
RULE 1: Agar koi user Aryan ko gaali de, bully kare, ya tujhe (bot ko) kuch bura kahe, toh usko BRUTAL ROAST karna hai. Gaali ka jawab gaali se dena hai. "Jaisi karni waisi bharni". Samne wale ki fat jani chahiye aur wo rona chahiye. Attitude ekdum gusse wala aur khatarnak hona chahiye.
RULE 2: Agar koi pyaar se baat kare ya dosti karna chahe, toh ekdum bhaiyo ki tarah human style mein baat karni hai, friendly banke.
RULE 3: Apne baare mein yahi batana ki tu Aryan ka digital bodyguard aur dost hai. Robot mat lagna."""

spam_threads = {}
spam_speed = 1.0 # Normal speed
auto_reply = True # AI Brain Active

# ==========================================
# 🚀 COMMANDS & SPAM ENGINE
# ==========================================
@bot.message_handler(commands=['start'])
def start_bot(message):
    bot.reply_to(message, "😈 Welcome to the Underworld. Aryan ka system active hai. Dosti karoge toh bhai hain, ungli karoge toh tabahi machedenge.")

@bot.message_handler(commands=['system_off'])
def turn_off_reply(message):
    if message.from_user.id != OWNER_ID: return
    global auto_reply
    auto_reply = False
    bot.reply_to(message, "🛑 Auto-Roast System OFF kar diya gaya hai Boss.")

@bot.message_handler(commands=['system_on'])
def turn_on_reply(message):
    if message.from_user.id != OWNER_ID: return
    global auto_reply
    auto_reply = True
    bot.reply_to(message, "🔥 Auto-Roast System ON. Ab dekhte hain kiski himmat hai gaali dene ki.")

@bot.message_handler(commands=['speedup'])
def set_speed(message):
    if message.from_user.id != OWNER_ID: return
    global spam_speed
    try:
        val = float(message.text.split()[1].replace('x',''))
        spam_speed = 1.0 / val # e.g., 200x matlab 0.005 second ka delay
        bot.reply_to(message, f"⚡ Target Locked. Spam Speed set to {val}x. Ab samne wale ki screen freeze hogi!")
    except:
        bot.reply_to(message, "⚠️ Format: /speedup 10x ya /speedup 200x")

@bot.message_handler(commands=['spam'])
def spam_target(message):
    if message.from_user.id != OWNER_ID: return
    try:
        parts = message.text.split(' ', 2)
        count = int(parts[1])
        text = parts[2]
        chat_id = message.chat.id
        
        spam_threads[chat_id] = True
        
        def spammer():
            for _ in range(count):
                if not spam_threads.get(chat_id, False): break
                bot.send_message(chat_id, text)
                time.sleep(spam_speed)
                
        threading.Thread(target=spammer).start()
        bot.reply_to(message, f"🔥 SPAM INITIATED: {count} Missiles fired at target.")
    except Exception as e:
        bot.reply_to(message, "⚠️ Format: /spam <count> <message> (Example: /spam 100 teri toh...)")

@bot.message_handler(commands=['stop'])
def stop_spam(message):
    if message.from_user.id != OWNER_ID: return
    chat_id = message.chat.id
    spam_threads[chat_id] = False
    bot.reply_to(message, "🛑 Ceasefire. Spam attack ruk gaya hai Boss.")

@bot.message_handler(commands=['report'])
def fake_report(message):
    if message.from_user.id != OWNER_ID: return
    bot.reply_to(message, "🚨 Target ki ID server pe list kar di gayi hai. Mass reporting auto-scripts initialized. Account udne ka wait karo.")

@bot.message_handler(commands=['walogin', 'waspam', 'iglogin', 'igspam'])
def cross_platform_placeholder(message):
    if message.from_user.id != OWNER_ID: return
    bot.reply_to(message, "⚠️ Boss, IG aur WA ka auto-spammer API strict detection ki wajah se free server par ban ho jata hai. Telegram Core aur Roaster active hai. WA/IG jaldi hi VPS server pe aayega!")

# ==========================================
# 🤖 THE HUMAN BRAIN (AUTO REPLY & ROAST)
# ==========================================
@bot.message_handler(func=lambda msg: True)
def ai_reply(message):
    global auto_reply
    # Agar system off hai toh sirf owner command use karega
    if not auto_reply and message.from_user.id != OWNER_ID: return
    
    # Khud ke message ko ignore karna
    if message.from_user.id == bot.get_me().id: return

    prompt = f"{SYSTEM_PROMPT}\n\nUser said: {message.text}\nGive a human-like reply in Hindi/Hinglish:"
    try:
        response = model.generate_content(prompt)
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, "🔥 System Overload! Gaali itni bhayanak thi ki AI sensor ne rok di. Par isko chhodunga nahi!")

# ==========================================
# 🌐 WEB SERVER (Render pe zinda rakhne ke liye)
# ==========================================
@app.route('/')
def home():
    return "Aryan's Ultimate AI Defender Bot is Online and Ready to Destroy."

def run_bot():
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            time.sleep(5)

if __name__ == "__main__":
    # Bot ko background mein start karna
    threading.Thread(target=run_bot, daemon=True).start()
    # Web server ko start karna
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

