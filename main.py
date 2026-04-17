import os, time, threading, random
import telebot
from telebot import types
import google.generativeai as genai
from flask import Flask

app = Flask(__name__)

# ==========================================
# 🔴 TITAN CREDENTIALS 🔴
# ==========================================
BOT_TOKEN = "8764748799:AAF_zK7dwMPycJeAY0rY_d6SW79r84wi5P4"
GEMINI_API_KEY = "AIzaSyAui3nTYj1WEvG-Tup-1RQXw3KzHHIhoXQ"
OWNER_ID = 8230119621

bot = telebot.TeleBot(BOT_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)

# Safety Settings (Brutal Mode)
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
]
model = genai.GenerativeModel('gemini-1.5-flash', safety_settings=safety_settings)

# ==========================================
# 🧠 ARYAN'S PERSONA (Human Mode)
# ==========================================
SYSTEM_PROMPT = """Tu koi AI nahi hai. Tu 'Aryan' ka hi ek digital roop hai. 
Details: Aryan, 16 Years Old, Jammu & Kashmir (J&K), Class 10th, Developer/Coder.
Attitude: Harami, Savage, Protective.
Rules:
1. Kabhi mat bolna ki tu AI hai ya model hai.
2. Baat aise kar jaise ek 16 saal ka ladka karta hai jo coder hai.
3. Groups mein shaant rehna hai jab tak boss na bole.
4. Jo Aryan ko gaali de, uski waat laga de (Savage roast/Slangs).
5. Jo pyaar se baat kare, wo bhai hai.
6. Identity: Tu Aryan ka digital bodyguard aur uska bhai hai."""

# Global Data
spam_messages = []
spam_active = False
spam_speed = 0.01  # 100x speed (Very low delay)

# ==========================================
# 🕹️ BUTTONS & MENU
# ==========================================
def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("➕ Add Msg", callback_data="add_msg")
    btn2 = types.InlineKeyboardButton("🗑️ Clear Msgs", callback_data="clear_msgs")
    btn3 = types.InlineKeyboardButton("🚀 Start Spam", callback_data="start_spam")
    btn4 = types.InlineKeyboardButton("🛑 Stop Spam", callback_data="stop_spam")
    btn5 = types.InlineKeyboardButton("📋 Show Msgs", callback_data="list_msgs")
    markup.add(btn1, btn2, btn3, btn4, btn5)
    return markup

@bot.message_handler(commands=['start', 'menu'])
def show_menu(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "Beta, baap se pange nahi. Aryan boss hi isse control kar sakte hain.")
        return
    bot.send_message(message.chat.id, "😈 *Titan Control Panel Active*", parse_mode="Markdown", reply_markup=main_menu())

# ==========================================
# ➕ MSG MANAGEMENT
# ==========================================
@bot.message_handler(commands=['add'])
def add_msg_manual(message):
    if message.from_user.id != OWNER_ID: return
    msg_text = message.text.replace('/add ', '').strip()
    if msg_text:
        spam_messages.append(msg_text)
        bot.reply_to(message, f"✅ Msg Added! Total Msgs: {len(spam_messages)}")
    else:
        bot.reply_to(message, "Usage: /add <bade bade messages>")

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    global spam_active, spam_messages
    if call.from_user.id != OWNER_ID: return

    if call.data == "add_msg":
        bot.send_message(call.message.chat.id, "Boss, message add karne ke liye type karo: `/add [Apka Message]`", parse_mode="Markdown")
    
    elif call.data == "clear_msgs":
        spam_messages = []
        bot.send_message(call.message.chat.id, "🗑️ Saare messages delete ho gaye!")
    
    elif call.data == "list_msgs":
        if not spam_messages:
            bot.send_message(call.message.chat.id, "List khali hai boss.")
        else:
            bot.send_message(call.message.chat.id, "📋 Current Msgs:\n\n" + "\n---\n".join(spam_messages))
            
    elif call.data == "start_spam":
        if not spam_messages:
            bot.send_message(call.message.chat.id, "⚠️ Pehle kuch messages add toh karo!")
        else:
            spam_active = True
            bot.send_message(call.message.chat.id, "🚀 100x Speed Attack Started!")
            threading.Thread(target=spam_engine, args=(call.message.chat.id,)).start()
            
    elif call.data == "stop_spam":
        spam_active = False
        bot.send_message(call.message.chat.id, "🛑 Attack Stopped.")

# ==========================================
# 🚀 100X SPAM ENGINE
# ==========================================
def spam_engine(chat_id):
    global spam_active
    while spam_active:
        if not spam_messages: break
        try:
            m = random.choice(spam_messages)
            bot.send_message(chat_id, m)
            time.sleep(spam_speed)
        except:
            time.sleep(1)

# ==========================================
# 💬 AI CHAT (Human Tone)
# ==========================================
@bot.message_handler(func=lambda msg: True)
def human_chat(message):
    # Boss commands handle karne ke liye
    if message.from_user.id == OWNER_ID and message.text.startswith('/'): return
    
    # Boss ne identity pooch li
    if "owner" in message.text.lower() or "malik" in message.text.lower():
        bot.reply_to(message, "Mere owner Aryan hain. J&K ke sher, 16 saal ki umar mein dev level ka kaam karte hain. Unse panga matlab maut se dosti.")
        return

    # Normal Chat
    prompt = f"{SYSTEM_PROMPT}\n\nUser: {message.text}\nAryan's Reply:"
    try:
        response = model.generate_content(prompt)
        bot.reply_to(message, response.text)
    except:
        bot.reply_to(message, "Beta, zyada mat bol. Aryan boss se keh ke block karwa dunga. 🔥")

# ==========================================
# 🌐 KEEP ALIVE
# ==========================================
@app.route('/')
def home(): return "Titan System Online"

def run_bot():
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except:
            time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
