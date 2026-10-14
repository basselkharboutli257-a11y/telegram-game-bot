import sqlite3
import telebot
from telebot import types
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# --- تشغيل خادم وهمي لإبقاء موقع Render نشطاً ولا يتوقف ---
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is active and running!")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

# تشغيل الخادم الوهمي في الخلفية
threading.Thread(target=run_web_server, daemon=True).start()
# ----------------------------------------------------

TOKEN = "8828639829:AAFdGAGzgpvA8aJFdDAyGxwrcYONp53CrEs"
bot = ebot.TeleBot(TOKEN)

def init_db():
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value REAL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER,
            category TEXT,
            name TEXT,
            price_usd REAL,
            FOREIGN KEY(game_id) REFERENCES games(id)
        )
    """)
    
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('exchange_rate', 15000)")
    
    cursor.execute("DELETE FROM products WHERE game_id = 1")
    cursor.execute("DELETE FROM games WHERE id = 1")
    
    cursor.execute("INSERT INTO games (id, name) VALUES (1, 'ببجي موبايل 🎮')")
    
    pubg_uc = [
        (1, 'شدات ببجي', '60 شدة', 0.99),
        (1, 'شدات ببجي', '325 شدة', 4.99),
        (1, 'شدات ببجي', '660 شدة', 9.99),
        (1, 'شدات ببجي', '1800 شدة', 24.99),
        (1, 'شدات ببجي', '3850 شدة', 49.69),
        (1, 'شدات ببجي', '8100 شدة', 99.90)
    ]
    
    pubg_subs = [
        (1, 'عضويات ببجي', 'حزمة الشراء الأولى', 1.50),
        (1, 'عضويات ببجي', 'حزمة ترقية الأسلحة', 3.50),
        (1, 'عضويات ببجي', 'حزمة شعار الأسطوري', 5.50),
        (1, 'عضويات ببجي', 'حزمة الشعار الخرافي الأسبوعية', 3.50),
        (1, 'عضويات ببجي', 'برايم شهر', 1.50),
        (1, 'عضويات ببجي', 'برايم بلس شهر', 11.00),
        (1, 'عضويات ببجي', 'برايم 3 أشهر', 3.50),
        (1, 'عضويات ببجي', 'برايم بلس 3 أشهر', 32.00),
        (1, 'عضويات ببجي', 'برايم 6 أشهر', 7.00),
        (1, 'عضويات ببجي', 'برايم بلس 6 أشهر', 64.00),
        (1, 'عضويات ببجي', 'برايم 12 شهر', 13.00),
        (1, 'عضويات ببجي', 'برايم بلس 12 شهر', 130.00),
        (1, 'عضويات ببجي', 'حزمة عروض أسبوعية 1', 1.50),
        (1, 'عضويات ببجي', 'حزمة عروض أسبوعية 2', 3.50),
        (1, 'عضويات ببجي', 'بطاقة نخبة مستوى 1', 7.00),
        (1, 'عضويات ببجي', 'بطاقة نخبة بلس مستوى 1', 32.00)
    ]
    
    cursor.executemany("INSERT INTO products (game_id, category, name, price_usd) VALUES (?, ?, ?, ?)", pubg_uc + pubg_subs)
    
    conn.commit()
    conn.close()

init_db()

def get_exchange_rate():
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key='exchange_rate'")
    rate = cursor.fetchone()[0]
    conn.close()
    return rate

def set_exchange_rate(new_rate):
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE settings SET value = ? WHERE key='exchange_rate'", (new_rate,))
    conn.commit()
    conn.close()

def get_categories(game_id):
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM products WHERE game_id = ?", (game_id,))
    categories = [row[0] for row in cursor.fetchall()]
    conn.close()
    return categories

def get_products_by_category(game_id, category):
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, price_usd FROM products WHERE game_id = ? AND category = ?", (game_id, category))
    products = cursor.fetchall()
    conn.close()
    return products

def main_menu():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🎮 قائمة الألعاب والخدمات", callback_data="show_games"))
    markup.add(types.InlineKeyboardButton("📊 استطلاع رأي", callback_data="start_poll"))
    markup.add(types.InlineKeyboardButton("📞 تواصل معنا", callback_data="contact_us"))
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        "أهلاً بك في بوت خدمات شحن الألعاب المتطور! 🕹️\nاختر ما يناسبك من القائمة أدناه:",
        reply_markup=main_menu()
    )

@bot.message_handler(commands=['setrate'])
def set_rate(message):
    args = message.text.split()
    if len(args) > 1:
        try:
            new_rate = float(args[1])
            set_exchange_rate(new_rate)
            bot.reply_to(message, f"✅ تم تحديث سعر الدولار بنجاح إلى: {new_rate}")
        except ValueError:
            bot.reply_to(message, "❌ خطأ: يرجى كتابة رقم صحيح لسعر الصرف.")
    else:
        bot.reply_to(message, "⚠️ الاستخدام الصحيح:\n`/setrate 15000`", parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "show_games":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("ببجي موبايل 🎮", callback_data="game_1"))
        markup.add(types.InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu"))
        bot.edit_message_text(
            "🎮 **اختر اللعبة المطلوبة:**",
            call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown"
        )

    elif call.data == "game_1":
        categories = get_categories(1)
        markup = types.InlineKeyboardMarkup()
        for cat in categories:
            markup.add(types.InlineKeyboardButton(cat, callback_data=f"cat_1_{cat}"))
        markup.add(types.InlineKeyboardButton("🔙 رجوع للألعاب", callback_data="show_games"))
        bot.edit_message_text(
            "📦 **اختر القسم المطلوب في ببجي موبايل:**",
            call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown"
        )

    elif call.data.startswith("cat_1_"):
        category_name = call.data.replace("cat_1_", "")
        rate = get_exchange_rate()
        products = get_products_by_category(1, category_name)
        
        text = f"🔹 **{category_name}**\n*(سعر الصرف المعتمد: {rate} ل.س)*\n\n"
        for name, price_usd in products:
            local_price = price_usd * rate
            text += f"▫️ **{name}**\n   💵 السعر: {price_usd}$ (~ {local_price:,.0f} ل.س)\n\n"

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 رجوع لأقسام ببجي", callback_data="game_1"))
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "start_poll":
        bot.send_poll(
            call.message.chat.id,
            question="ما هي اللعبة التي تود أن توفر لها عروض شحن إضافية؟",
            options=["ببجي موبايل (PUBG)", "فري فاير (Free Fire)", "كلاش أوف كلانس (CoC)", "ألعاب أخرى"],
            is_anonymous=False
        )

    elif call.data == "contact_us":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu"))
        bot.edit_message_text(
            "📞 لإتمام عمليات الشحن، يرجى التواصل معنا عبر المعرف الخاص بالمتجر.",
            call.message.chat.id, call.message.message_id, reply_markup=markup
        )

    elif call.data == "main_menu":
        bot.edit_message_text(
            "أهلاً بك مجدداً في القائمة الرئيسية:",
            call.message.chat.id, call.message.message_id, reply_markup=main_menu()
        )

print("Bot is running...")
bot.infinity_polling()
