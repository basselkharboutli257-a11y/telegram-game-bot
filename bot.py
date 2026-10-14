import sqlite3
import telebot
from telebot import types

TOKEN = "8828639829:AAFdGAGzgpvA8aJFdDAyGxwrcYONp53CrEs"
bot = telebot.TeleBot(TOKEN)

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
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            price_usd REAL
        )
    """)
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('exchange_rate', 15000)")
    
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        sample_products = [
            ("شدات ببجي 660 UC", 9.99),
            ("جواهر فري فاير 1080", 8.50),
            ("شدات ببجي 325 UC", 4.99)
        ]
        cursor.executemany("INSERT INTO products (name, price_usd) VALUES (?, ?)", sample_products)
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

def get_products():
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, price_usd FROM products")
    products = cursor.fetchall()
    conn.close()
    return products

def main_menu():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🎮 قائمة الألعاب والأسعار", callback_data="show_products"))
    markup.add(types.InlineKeyboardButton("📊 استطلاع رأي", callback_data="start_poll"))
    markup.add(types.InlineKeyboardButton("📞 تواصل معنا", callback_data="contact_us"))
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        "أهلاً بك في بوت خدمات شحن الألعاب! 🕹️\nاختر من الأدناه ما يناسبك:",
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
    if call.data == "show_products":
        rate = get_exchange_rate()
        products = get_products()
        text = f"📦 **قائمة المنتجات والأسعار الحالية**\n*(سعر الصرف المعتمد: {rate} ل.س)*\n\n"
        for name, price_usd in products:
            local_price = price_usd * rate
            text += f"🔹 **{name}**\n   السعر: {price_usd}$ (~ {local_price:,.0f} ل.س)\n\n"
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu"))
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
            "📞 لإتمام عمليات الشحن، يرجى التواصل معنا.",
            call.message.chat.id, call.message.message_id, reply_markup=markup
        )

    elif call.data == "main_menu":
        bot.edit_message_text(
            "أهلاً بك مجدداً في القائمة الرئيسية:",
            call.message.chat.id, call.message.message_id, reply_markup=main_menu()
        )

print("Bot is running...")
bot.infinity_polling()
