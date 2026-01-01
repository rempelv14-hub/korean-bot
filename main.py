import asyncio
import os
import logging
from datetime import datetime, timedelta
from threading import Thread

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.exceptions import TelegramAPIError, RetryAfter

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from tzlocal import get_localzone

from flask import Flask

# ================== ЛОГИРОВАНИЕ ==================
logging.basicConfig(level=logging.INFO)

# ================== ТОКЕН ==================
BOT_TOKEN = os.environ.get("BOT_TOKEN")  # <- только имя переменной окружения

if not BOT_TOKEN:
    logging.error("⚠️ BOT_TOKEN не найден! Проверь Worker Variables на Railway.")
    BOT_TOKEN = None  # Бот не будет запускаться, но код не упадет

# ================== MEDIA ==================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEDIA_DIR = os.path.join(BASE_DIR, "media")
VIDEO_URL = "https://youtu.be/uKKyn7wCKXE?si=Klz0s_l-jsvJCVTv"

def find_pdf():
    if not os.path.exists(MEDIA_DIR):
        return None
    for file in os.listdir(MEDIA_DIR):
        if file.lower().endswith(".pdf"):
            return os.path.join(MEDIA_DIR, file)
    return None

PDF_PATH = find_pdf()
logging.info(f"PDF найден: {PDF_PATH}")

# ================== КНОПКИ ==================
start_kb = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="🚀 Старт", callback_data="start_course")]]
)

course_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Оформить тариф «Стандарт»", url="https://t.me/tribute/app?startapp=sK0H")],
        [InlineKeyboardButton(text="Оформить тариф «VIP»", url="https://t.me/tribute/app?startapp=sK0H")]
    ]
)

subscription_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Оформить подписку", url="https://t.me/tribute/app?startapp=sK0H")]
    ]
)

fifth_message_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Оплатить «Стандарт»", url="https://web.tribute.tg/s/K0H")],
        [InlineKeyboardButton(text="Оплатить «VIP»", url="https://t.me/minimalkor")],
        [InlineKeyboardButton(text="Подписаться на канал", url="https://t.me/minimalkorean")]
    ]
)

# ================== BOT ==================
bot = Bot(token=BOT_TOKEN) if BOT_TOKEN else None
dp = Dispatcher()
router = Router()
dp.include_router(router)

# ================== SCHEDULER ==================
scheduler = AsyncIOScheduler(timezone=get_localzone())

# ================== ГЛОБАЛЬНЫЕ ДАННЫЕ ==================
active_users = {}  # user_id -> {"paid": bool, "jobs": [scheduler_job]}

# ================== СООБЩЕНИЯ ==================
async def send_video(message: Message):
    try:
        await message.answer(
            "Отлично! Начнём с подарка 🎁\n"
            "Я подготовила видео о том, как правильно планировать изучение корейского,\n"
            "чтобы не бросить через неделю и не тратить время впустую.\n\n"
            f"👉 Смотри видео: {VIDEO_URL}\n"
            "После просмотра тебя ждёт ещё один бонус ✨\n(я пришлю его чуть позже)"
        )
    except Exception as e:
        logging.error(f"Ошибка при отправке видео: {e}")

async def send_pdf(message: Message):
    try:
        await message.answer(
            "Как и обещала — вот твой бонус 📘✨\n"
            "Дарю календарь для изучения корейского.\n"
            "Он поможет дойти до 4го уровня системно и без срывов."
        )
        if PDF_PATH and os.path.exists(PDF_PATH):
            await message.answer_document(FSInputFile(PDF_PATH))
        else:
            await message.answer("⚠️ PDF не найден")
    except Exception as e:
        logging.error(f"Ошибка при отправке PDF: {e}")

async def send_course_presentation(message: Message):
    try:
        text = (
            "А все что в календаре, что ждёт тебя на курсе Система KOREAN MINIMAL 👇\n"
            "... (текст сохранен без изменений) ..."
        )
        await message.answer(text, reply_markup=course_kb)
    except Exception as e:
        logging.error(f"Ошибка при отправке презентации курса: {e}")

async def send_useful_tips(message: Message):
    try:
        await message.answer(
            "Начнём сразу с самого полезного 🔥\n..."
            , reply_markup=fifth_message_kb
        )
    except Exception as e:
        logging.error(f"Ошибка при отправке полезных советов: {e}")

async def send_final_message(message: Message):
    try:
        await message.answer(
            "Еще один шаг и ты студент KOREAN MINIMAL\n..."
            , reply_markup=subscription_kb
        )
    except Exception as e:
        logging.error(f"Ошибка при отправке финального сообщения: {e}")

# ================== ФУНКЦИЯ ЦЕПОЧКИ ==================
def schedule_chain(user_id: int, message: Message):
    jobs = []

    async def send_if_not_paid(func, msg):
        if user_id not in active_users:
            active_users[user_id] = {"paid": False, "jobs": []}

        if not active_users[user_id]["paid"]:
            try:
                await func(msg)
            except Exception as e:
                logging.error(f"Ошибка при отправке сообщения пользователю {msg.from_user.id}: {e}")
        else:
            for job in active_users[user_id]["jobs"]:
                job.remove()
            active_users[user_id]["jobs"] = []

    now = datetime.now(get_localzone())

    message_chain = [
        (send_pdf, timedelta(minutes=5)),
        (send_course_presentation, timedelta(minutes=10)),
        (send_useful_tips, timedelta(hours=3)),
        (send_final_message, timedelta(days=3)),
    ]

    for func, delta in message_chain:
        job = scheduler.add_job(send_if_not_paid, DateTrigger(now + delta), args=[func, message])
        jobs.append(job)

    active_users[user_id]["jobs"] = jobs

# ================== ХЕНДЛЕРЫ ==================
@router.message(CommandStart())
async def start(message: Message):
    user_id = message.from_user.id
    if user_id not in active_users:
        active_users[user_id] = {"paid": False, "jobs": []}

    await message.answer(
        "안녕하세요!\n..."
        , reply_markup=start_kb
    )

@router.callback_query(F.data == "start_course")
async def start_course(callback: CallbackQuery):
    user_id = callback.from_user.id
    await callback.answer()

    if active_users[user_id]["jobs"]:
        await callback.message.answer(
            "Вы уже запустили курс! ⏳\n..."
        )
        return

    await send_video(callback.message)
    schedule_chain(user_id, callback.message)

@router.callback_query(F.data.startswith("pay_"))
async def handle_payment(callback: CallbackQuery):
    user_id = callback.from_user.id
    active_users[user_id]["paid"] = True

    for job in active_users[user_id]["jobs"]:
        job.remove()
    active_users[user_id]["jobs"] = []

    await callback.message.answer(
        f"Вы выбрали тариф ✅\nПожалуйста, отправьте чек оплаты в Telegram: https://t.me/minimalkor"
    )

# ================== ЗАПУСК ==================
async def start_bot():
    scheduler.start()
    if bot:
        await dp.start_polling(bot)
    else:
        logging.warning("BOT_TOKEN отсутствует, бот не запущен.")

# ================== FLASK ==================
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

if __name__ == "__main__":
    Thread(target=lambda: asyncio.run(start_bot())).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
