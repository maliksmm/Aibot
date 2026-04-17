import os, time, threading, random
import telebot
from telebot import types
import google.generativeai as genai
from flask import Flask

app = Flask(__name__)

# ==========================================
# 🔴 ARYAN'S ULTIMATE CREDENTIALS 🔴
# ==========================================
BOT_TOKEN = "8764748799:AAF_zK7dwMPycJeAY0rY_d6SW79r84wi5P4"
GEMINI_API_KEY = "AIzaSyAui3nTYj1WEvG-Tup-1RQXw3KzHHIhoXQ"
OWNER_ID = 8230119621 # Aryan's ID

bot = telebot.TeleBot(BOT_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)

# AI Model Setup (No Filters)
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
]
model = genai.GenerativeModel('gemini-1.5-flash', safety_settings=safety_settings)

# ==========================================
# 🧠 ARYAN'S BRAIN (The Persona)
# ==========================================
SYSTEM_PROMPT = """Tu koi AI nahi hai. Tu 'Aryan' ka personal bodyguard aur uska twin brother hai.
Aryan ki details: 16 years, J&K, Class 10th, Dev/Coder.
Attitude: Full Savage, Aggressive toward enemies, Loyal to Aryan.
Instructions:
1. Sirf Aryan ke orders maanega.
2. Koi aur order de toh bolna: 'Aukaat mein reh, baap ko mat sikha. Sirf Aryan Boss ka hukum chalta hai.'
3. Roast aise kar ki samne wala social media chhod de.
4. Human ki tarah lambi baat kar, 1 word replies mat de.
5. Robot, AI, ya Large Language Model jaise words kabhi mat bolna."""

# Global States
spam_active = {}
spam_messages = ["TABAHI START 🔥", "TERI WAAT LAG GAYI 💀", "ARYAN BOSS KA SYSTEM HAI ⚔️"]
pending_approvals = {}

# ==========================================
# 🛡️ COMMANDS LOGIC
# ==========================================

@bot.message_handler(commands=['start', 'menu'])
def welcome(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "Beta, Aryan Boss ke bot se door raho warna system hang ho jayega tera.")
        return
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("➕ Add Msgs", callback_data="add_msg"),
        types.InlineKeyboardButton("📋 List Msgs", callback_data="list_msgs"),
        types.InlineKeyboardButton("🗑️ Clear All", callback_data="clear_msgs"),
        types.InlineKeyboardButton("🛑 Global Stop", callback_data="stop_all")
    )
    bot.send_message(message.chat.id, f"👋 Welcome Aryan Boss.\n\n*Spam Commands:* \n`/spamtg [link/username] [time]`\n`/spamig [target] [time]`\n`/spamwp [link] [time]`\n\n*Group Command:* `strt nc` (Group mein tabahi)", parse_mode="Markdown", reply_markup=markup)

# --- Approval System ---
def ask_approval(target, platform, duration, owner_msg_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ APPROVE", callback_data=f"app_{owner_msg_id}"),
        types.InlineKeyboardButton("❌ REJECT", callback_data=f"rej_{owner_msg_id}")
    )
    pending_approvals[owner_msg_id] = {"target": target, "platform": platform, "duration": duration}
    bot.send_message(OWNER_ID, f"🚨 *SPAM REQUEST*\n\nTarget: `{target}`\nPlatform: `{platform}`\nTime: `{duration}`\n\nBoss, approve karoge toh hi start karunga!", parse_mode="Markdown", reply_markup=markup)

# --- Spammer Engine ---
def start_heavy_spam(chat_id, target, platform):
    spam_active[chat_id] = True
    while spam_active.get(chat_id):
        if not spam_messages: break
        try:
            m = random.choice(spam_messages)
            # 100 msgs/sec loop simulation
            for _ in range(10): # Batches to bypass internal bottleneck
                bot.send_message(chat_id, f"[{platform.upper()} ATTACK] {target}\n\n{m}")
            time.sleep(0.01) # Ultra fast delay
        except Exception as e:
            time.sleep(1)

# --- Commands Implementation ---
@bot.message_handler(commands=['spamtg', 'spamig', 'spamwp'])
def handle_spam_cmds(message):
    if message.from_user.id != OWNER_ID: return
    try:
        parts = message.text.split()
        target = parts[1]
        duration = parts[2] if len(parts) > 2 else "Lifetime"
        platform = message.text.split()[0][5:] # tg, ig, or wp
        
        bot.reply_to(message, f"⏳ Requesting login & approval for {platform.upper()}... Check your DM Boss.")
        ask_approval(target, platform, duration, message.message_id)
    except:
        bot.reply_to(message, "Usage: `/spamtg @username 1year`", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text and m.text.lower() == "strt nc")
def group_nc(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "Aukaat mein reh, sirf Aryan Boss bol sakte hain.")
        return
    bot.reply_to(message, "🔥 Non-Stop Attack Started in this Group!")
    start_heavy_spam(message.chat.id, "GROUP_NC", "Telegram")

@bot.message_handler(commands=['stop'])
def stop_all_cmd(message):
    if message.from_user.id != OWNER_ID: return
    spam_active[message.chat.id] = False
    bot.reply_to(message, "🛑 Attack Stopped.")

# ==========================================
# 🕹️ CALLBACK HANDLERS
# ==========================================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    global spam_messages
    if call.from_user.id != OWNER_ID: return

    if call.data.startswith("app_"):
        msg_id = int(call.data.split("_")[1])
        task = pending_approvals.get(msg_id)
        if task:
            bot.edit_message_text(f"🚀 *ATTACK APPROVED*\nLogging into {task['platform']}... Starting Spam on {task['target']}", OWNER_ID, call.message.id, parse_mode="Markdown")
            threading.Thread(target=start_heavy_spam, args=(call.message.chat.id, task['target'], task['platform'])).start()
    
    elif call.data == "add_msg":
        bot.send_message(call.message.chat.id, "Boss, /add ke baad apna message likho.")
    
    elif call.data == "clear_msgs":
        spam_messages = []
        bot.answer_callback_query(call.id, "List Cleared!")

# ==========================================
# 💬 AI CHAT & ROAST
# ==========================================
@bot.message_handler(func=lambda message: True)
def smart_reply(message):
    # Ignore commands
    if message.text.startswith('/'): return
    
    # Roast logic if someone talks shit to Aryan
    user_msg = message.text.lower()
    
    if message.from_user.id != OWNER_ID:
        prompt = f"{SYSTEM_PROMPT}\n\nUser: {message.text}\nRoast this person brutally because he is talking to Aryan's Bot without permission:"
    else:
        # If Aryan Boss talks
        if "add msg" in user_msg or "/add" in user_msg:
            new_m = message.text.replace('/add', '').strip()
            if new_m:
                spam_messages.append(new_m)
                bot.reply_to(message, "✅ New Bomb added to Arsenal!")
            return
        prompt = f"{SYSTEM_PROMPT}\n\nBoss Aryan said: {message.text}\nReply like a loyal brother:"

    try:
        response = model.generate_content(prompt)
        bot.reply_to(message, response.text)
    except:
        bot.reply_to(message, "Beta, Aryan Boss se panga mat le warna maut pakki hai teri. 💀")

# ==========================================
# 🌐 DEPLOYMENT
# ==========================================
@app.route('/')
def home(): return "Aryan's God-Mode Active"

def run_bot():
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except: time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
