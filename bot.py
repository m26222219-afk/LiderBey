import telebot
import json
import os
import requests
from telebot import types

# --- AYARLAR ---
TOKEN = "8317785009:AAE6orG0-1SF19GXOyq7pabbOOjt1cjco-E"
KANAL_USERNAME = "@LBduyuru"
# Senin GitHub Raw Linkin:
GITHUB_URL = "https://raw.githubusercontent.com/m26222219-afk/LiderBey/main/gorevler.json"

bot = telebot.TeleBot(TOKEN)
DB_FILE = "users.json"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f: return json.loads(f.read())
        except: return {}
    return {}

def save_data(data):
    with open(DB_FILE, "w") as f: json.dump(data, f, indent=4)

users = load_data()

def get_remote_tasks():
    try:
        response = requests.get(GITHUB_URL)
        return response.json()
    except:
        return {}

@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)
    if user_id not in users:
        users[user_id] = {'puan': 0, 'davet': 0, 'tamamlanan': []}
        save_data(users)
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🔗 GÖREV LİSTESİ", callback_data="liste"),
        types.InlineKeyboardButton("🔑 KODU BOZDUR", callback_data="kod_gir"),
        types.InlineKeyboardButton("👥 DAVET ET", callback_data="davet"),
        types.InlineKeyboardButton("📊 HESABIM / MARKET", callback_data="market")
    )
    bot.send_message(message.chat.id, "🏦 **KOD BANKASI - HOŞ GELDİN!**\n\nLinkleri geç, puanları topla, ödülleri kap!", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    user_id = str(call.from_user.id)
    tasks = get_remote_tasks()
    
    if call.data == "liste":
        markup = types.InlineKeyboardMarkup(row_width=2)
        buttons = []
        if not tasks:
            bot.answer_callback_query(call.id, "⚠️ Görevler yüklenemedi, GitHub linkini kontrol et!")
            return
        
        for g_id, g_info in tasks.items():
            status = "✅" if g_id in users[user_id].get('tamamlanan', []) else "💎"
            buttons.append(types.InlineKeyboardButton(f"{status} {g_id.upper()}", url=g_info['link']))
        
        markup.add(*buttons)
        bot.edit_message_text("📝 **GÖREV LİSTESİ**\nLinkleri geç, kodu al ve aşağıdaki butondan bozdur!", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data == "kod_gir":
        msg = bot.send_message(call.message.chat.id, "🔑 Geçtiğin linkin sonundaki kodu yaz:")
        bot.register_next_step_handler(msg, kod_onay)

    elif call.data == "market":
        txt = f"📊 **HESABIM**\n💰 Puanın: {users[user_id]['puan']}\n\n🛒 **MARKET**\n- 25 TL Play Kodu: 250 Puan\n- 60 UC: 300 Puan\n\nÖdül almak için: @LiderrBeyy"
        bot.send_message(call.message.chat.id, txt)

    elif call.data == "davet":
        link = f"https://t.me/{bot.get_me().username}?start={user_id}"
        bot.send_message(call.message.chat.id, f"👥 Her davet: 10 Puan\nLinkin: `{link}`")

def kod_onay(message):
    user_id = str(message.from_user.id)
    kod = message.text.strip().upper()
    tasks = get_remote_tasks()
    
    bulundu = False
    for g_id, g_info in tasks.items():
        if kod == g_info['kod'].upper():
            if g_id in users[user_id]['tamamlanan']:
                bot.send_message(message.chat.id, "⚠️ Bu görevi zaten yapmışsın!")
            else:
                users[user_id]['puan'] += g_info['puan']
                users[user_id]['tamamlanan'].append(g_id)
                save_data(users)
                bot.send_message(message.chat.id, f"✅ DOĞRU! +{g_info['puan']} Puan.")
            bulundu = True
            break
            
    if not bulundu:
        bot.send_message(message.chat.id, "❌ Yanlış kod girdin!")

bot.infinity_polling()
