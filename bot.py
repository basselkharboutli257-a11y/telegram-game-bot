import sqlite3
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

#
TOKEN = "8719921976:AAE-g6J0le062uM5AQn4iKEbiZ7mw_3wLKY"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- إعداد قاعدة البيانات ---
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
    cursor.cursor()
    cursor = conn.cursor()
    cursor.execute("SELECT name, price_usd FROM products")
    products = cursor.fetchall()
    conn.close()
    return products

def main_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="🎮 قائمة الألعاب والأسعار", callback_data="show_products")
    builder.button(text="📊 استطلاع رأي", callback_data="start_poll")
    builder.button(text="📞 تواصل معنا", callback_data="contact_us")
    builder.adjust(1)
    return builder.as_markup()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "أهلاً بك في بوت خدمات شحن الألعاب! 🕹️\nاختر من الأدناه ما يناسبك:",
        reply_markup=main_menu()
    )

@dp.message(Command("setrate"))
async def cmd_set_rate(message: types.Message):
    args = message.text.split()
    if len(args) > 1:
        try:
            new_rate = float(args[1])
            set_exchange_rate(new_rate)
            await message.answer(f"✅ تم تحديث سعر الدولار بنجاح إلى: {new_rate}")
        except ValueError:
            await message.answer("❌ خطأ: يرجى كتابة رقم صحيح لسعر الصرف.")
    else:
        await message.answer("⚠️ الاستخدام الصحيح:\n`/setrate 15000`", parse_mode="Markdown")

@dp.callback_query(F.data == "show_products")
async def show_products_callback(callback: types.CallbackQuery):
    rate = get_exchange_rate()
    products = get_products()
    
    text = f"📦 **قائمة المنتجات والأسعار الحالية**\n*(سعر الصرف المعتمد: {rate} ل.س)*\n\n"
    for name, price_usd in products:
        local_price = price_usd * rate
        text += f"🔹 **{name}**\n   السعر: {price_usd}$ (~ {local_price:,.0f} ل.س)\n\n"
        
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 القائمة الرئيسية", callback_data="main_menu")
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "start_poll")
async def start_poll_callback(callback: types.CallbackQuery):
    await callback.message.answer_poll(
        question="ما هي اللعبة التي تود أن توفر لها عروض شحن إضافية؟",
        options=["ببجي موبايل (PUBG)", "فري فاير (Free Fire)", "كلاش أوف كلانس (CoC)", "ألعاب أخرى"],
        is_anonymous=False
    )
    await callback.answer()

@dp.callback_query(F.data == "contact_us")
async def contact_callback(callback: types.CallbackQuery):
    builder.button(text="🔙 القائمة الرئيسية", callback_data="main_menu")
    # يمكنك استبدال معرفك هنا
    await callback.message.edit_text(
        "📞 لاتمام عمليات الشحن، يرجى التواصل مع الإدارة عبر المعرف:",
        reply_markup=builder.as_markup()
    )
    await callback.answer()

@dp.callback_query(F.data == "main_menu")
async def back_to_main(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "أهلاً بك مجدداً في القائمة الرئيسية:",
        reply_markup=main_menu()
    )
    await callback.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
      
