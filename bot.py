import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiohttp import web
import os

# ===== НАСТРОЙКИ =====
BOT_TOKEN = "8589282060:AAElMSQcx9sdr4RjisTKuu2mNsl_XbmbSjA"
ADMIN_CHAT_ID = 5187923987

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ===== СОСТОЯНИЯ =====
class Form(StatesGroup):
    name = State()
    phone = State()
    service = State()
    time = State()
    confirm = State()

# ===== КЛАВИАТУРЫ =====
def main_menu():
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🦷 Записатися на прийом")],
            [KeyboardButton(text="💰 Ціни та послуги")],
            [KeyboardButton(text="📍 Адреса та графік")],
            [KeyboardButton(text="📞 Зв'язатися з адміністратором")],
        ],
        resize_keyboard=True
    )
    return kb

def services_menu():
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Консультація")],
            [KeyboardButton(text="Лікування карієсу")],
            [KeyboardButton(text="Чистка зубів")],
            [KeyboardButton(text="Імплантація")],
            [KeyboardButton(text="Брекети / вирівнювання")],
            [KeyboardButton(text="⬅️ Назад")],
        ],
        resize_keyboard=True
    )
    return kb

def time_menu():
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Зранку (9:00–12:00)")],
            [KeyboardButton(text="Вдень (12:00–16:00)")],
            [KeyboardButton(text="Ввечері (16:00–19:00)")],
            [KeyboardButton(text="⬅️ Назад")],
        ],
        resize_keyboard=True
    )
    return kb

def confirm_menu():
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Підтвердити")],
            [KeyboardButton(text="❌ Скасувати")],
        ],
        resize_keyboard=True
    )
    return kb

# ===== СТАРТ =====
@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        f"Вітаємо у стоматології «ОРТЕКС-СТ»! 🦷\n\n"
        f"Я — ваш помічник. Допоможу записатися на прийом, "
        f"розповім про послуги та ціни.\n\n"
        f"Оберіть, будь ласка, що вас цікавить:",
        reply_markup=main_menu()
    )

# ===== ИНФО-БЛОКИ =====
@dp.message(F.text == "💰 Ціни та послуги")
async def prices(message: Message):
    await message.answer(
        "💰 <b>Наші послуги та орієнтовні ціни:</b>\n\n"
        "• Консультація — 300 грн\n"
        "• Лікування карієсу — від 1200 грн\n"
        "• Чистка зубів (ультразвук) — 900 грн\n"
        "• Імплантація — від 15000 грн\n"
        "• Брекети — від 25000 грн\n\n"
        "Точну вартість лікар визначить після огляду.\n"
        "Записатися на консультацію?",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )

@dp.message(F.text == "📍 Адреса та графік")
async def address(message: Message):
    await message.answer(
        "📍 <b>Ми тут:</b>\n"
        "м. Полтава, вул. Шевченка, 12\n\n"
        "🕐 <b>Графік роботи:</b>\n"
        "Пн–Пт: 9:00–19:00\n"
        "Сб: 9:00–15:00\n"
        "Нд: вихідний\n\n"
        "Записатися на прийом?",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )

@dp.message(F.text == "📞 Зв'язатися з адміністратором")
async def contact_admin(message: Message):
    await message.answer(
        "📞 <b>Контакти адміністратора:</b>\n"
        "Телефон: +38 (099) 123-45-67\n"
        "Telegram: @orteks_admin\n\n"
        "Або залиште заявку — ми вам зателефонуємо.",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )

# ===== ЗАПИСЬ НА ПРИЙОМ =====
@dp.message(F.text == "🦷 Записатися на прийом")
async def start_booking(message: Message, state: FSMContext):
    await state.set_state(Form.name)
    await message.answer(
        "Чудово! Давайте запишемо вас на прийом.\n\n"
        "Як вас звати? (Ім'я та прізвище)",
        reply_markup=ReplyKeyboardRemove()
    )

@dp.message(Form.name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Form.phone)
    await message.answer(
        f"Дякую, {message.text}!\n\n"
        "Вкажіть, будь ласка, ваш номер телефону у форматі +380XXXXXXXXX:"
    )

@dp.message(Form.phone)
async def get_phone(message: Message, state: FSMContext):
    phone = message.text.strip()
    if not phone.startswith("+380") or len(phone) != 13:
        await message.answer(
            "Будь ласка, введіть номер у форматі +380XXXXXXXXX (12 цифр після +)."
        )
        return
    await state.update_data(phone=phone)
    await state.set_state(Form.service)
    await message.answer(
        "Яка послуга вас цікавить?",
        reply_markup=services_menu()
    )

@dp.message(Form.service)
async def get_service(message: Message, state: FSMContext):
    if message.text == "⬅️ Назад":
        await state.set_state(Form.phone)
        await message.answer("Вкажіть ваш номер телефону у форматі +380XXXXXXXXX:")
        return
    await state.update_data(service=message.text)
    await state.set_state(Form.time)
    await message.answer(
        "Коли вам зручно прийти?",
        reply_markup=time_menu()
    )

@dp.message(Form.time)
async def get_time(message: Message, state: FSMContext):
    if message.text == "⬅️ Назад":
        await state.set_state(Form.service)
        await message.answer("Яка послуга вас цікавить?", reply_markup=services_menu())
        return
    await state.update_data(time=message.text)
    await state.set_state(Form.confirm)

    data = await state.get_data()
    await message.answer(
        "Перевірте, будь ласка, дані:\n\n"
        f"👤 Ім'я: {data['name']}\n"
        f"📱 Телефон: {data['phone']}\n"
        f"🦷 Послуга: {data['service']}\n"
        f"🕐 Час: {data['time']}\n\n"
        "Все вірно?",
        reply_markup=confirm_menu()
    )

@dp.message(Form.confirm)
async def confirm(message: Message, state: FSMContext):
    if message.text == "❌ Скасувати":
        await state.clear()
        await message.answer(
            "Запис скасовано. Якщо передумаєте — я завжди тут.",
            reply_markup=main_menu()
        )
        return

    data = await state.get_data()
    await state.clear()

    # Отправка заявки админу
    admin_text = (
        "🦷 <b>НОВА ЗАЯВКА НА ПРИЙОМ</b>\n\n"
        f"👤 Ім'я: {data['name']}\n"
        f"📱 Телефон: {data['phone']}\n"
        f"🦷 Послуга: {data['service']}\n"
        f"🕐 Час: {data['time']}"
    )
    await bot.send_message(ADMIN_CHAT_ID, admin_text, parse_mode="HTML")

    await message.answer(
        "✅ <b>Дякуємо! Вашу заявку прийнято.</b>\n\n"
        "Адміністратор зв'яжеться з вами найближчим часом, "
        "щоб підтвердити точний час візиту.\n\n"
        "Гарного дня! 🦷",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )

# ===== ОБРАБОТКА НЕИЗВЕСТНЫХ СООБЩЕНИЙ =====
@dp.message()
async def unknown(message: Message):
    await message.answer(
        "Не зрозумів вас. Оберіть, будь ласка, пункт з меню 👇",
        reply_markup=main_menu()
    )

# ===== ЗАПУСК =====
async def main():
    print("Бот запущен...")
    
    # Фейковый веб-сервер для Render (чтобы он видел открытый порт)
    app = web.Application()
    app.router.add_get("/", lambda r: web.Response(text="Bot is alive!"))
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    # Сам бот
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
if __name__ == "__main__":
    asyncio.run(main())
