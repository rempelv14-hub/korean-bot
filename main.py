import asyncio
import os
import logging

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    FSInputFile,
)

from aiohttp import web

# ================== ЛОГИ ==================
logging.basicConfig(level=logging.INFO)

# ================== ТОКЕН ==================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise SystemExit("❌ BOT_TOKEN не найден")

# ================== MEDIA ==================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEDIA_DIR = os.path.join(BASE_DIR, "media")
VIDEO_URL = "https://youtu.be/uKKyn7wCKXE?si=Klz0s_l-jsvJCVTv"

def find_pdf():
    if not os.path.exists(MEDIA_DIR):
        return None
    for f in os.listdir(MEDIA_DIR):
        if f.lower().endswith(".pdf"):
            return os.path.join(MEDIA_DIR, f)
    return None

PDF_PATH = find_pdf()

# ================== BOT ==================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# ================== КНОПКИ ==================
start_kb = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="🚀 Старт", callback_data="start_course")]]
)

fifth_message_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Оплатить «Стандарт»", url="https://web.tribute.tg/s/K0H")],
        [InlineKeyboardButton(text="Оплатить «VIP»", url="https://t.me/minimalkor")],
    ]
)

sixth_message_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Оформить подписку", url="https://t.me/tribute/app?startapp=sK0H")]
    ]
)

# ================== СООБЩЕНИЯ ==================
async def send_first(message: Message):
    await message.answer(
        "안녕하세요!\n"
        "Рада приветствовать тебя! Я — твой персональный бот-помощник корейского\n"
        "языка 🇰🇷\n"
        "Система KOREAN MINIMAL - это новый практический курс о том, как:\n"
        "• учить корейский системно, уделяя минимум времени;\n"
        "• научиться быстро и правильно читать и писать;\n"
        "• легко запоминать слова и грамматику;\n"
        "• двигаться без хаоса и перегруза.\n"
        "Готов(а) начать путь к корейскому, который действительно работает🇰🇷",
        reply_markup=start_kb,
    )

async def send_second(message: Message):
    await message.answer(
        "Отлично! Начнём с подарка 🎁\n"
        "Я подготовила видео о том, как правильно планировать изучение корейского,\n"
        "чтобы не бросить через неделю и не тратить время впустую.\n\n"
        f"👉 Смотри видео: {VIDEO_URL}\n"
        "После просмотра тебя ждёт ещё один бонус ✨\n(я пришлю его чуть позже)"
    )

async def send_third(message: Message):
    await message.answer(
        "Как и обещала — вот твой бонус 📘✨\n"
        "Дарю календарь для изучения корейского.\n"
        "Он поможет дойти до 4го уровня системно и без срывов."
    )
    if PDF_PATH:
        await message.answer_document(FSInputFile(PDF_PATH))

# ================== 4 СООБЩЕНИЕ (ТОЛЬКО ФОРМАТИРОВАНИЕ) ==================
async def send_fourth(message: Message):
    await message.answer(
        "А все что в календаре,ждёт тебя на курсе Система KOREAN MINIMAL 👇\n\n"
        
        "На курсе за месяц ты:\n\n"
        "▫️научишься быстро и правильно читать;\n"
        "▫️начнёшь красиво писать и понимать логику языка;\n"
        "▫️создашь личный план изучения корейского, который реально работает;\n"
        "▫️начнёшь говорить на корейском уже в процессе обучения.\n\n\n"

        
        "Курс состоит из 4 модулей:\n\n"
        "🔹 Модуль 1 — Чтение\n"
        "Освоение ассимиляции и произношения.\n\n"
        "🔹 Модуль 2 — Словарный запас (300 слов)\n"
        "Методы, практика, использование в диалогах.\n\n"
        "🔹 Модуль 3 — Говорить без страха\n"
        "Построение фраз, уверенная речь.\n\n"
        "🔹 Модуль 4 — Скорочтение\n"
        "Быстрое понимание текста и развитие скорости чтения.\n\n\n"

        
        "Тариф “стандарт” включает:\n\n"
        "📌 Большие выпуски о методах и правильном чтении\n"
        "📌 16 уроков по словарному запасу\n"
        "📌 8 уроков грамматики\n"
        "📌 Видео-разборы корейских песен\n"
        "📌 Марафон по словам и разговорной практике\n"
        "📌 Обратная связь\n\n"
        "Цена: 12990 тенге/ 1990 ₽ в месяц\n\n\n"

        
        "Тариф “VIP” включает:\n\n"
        "📌 Большие выпуски о методах и правильном чтении\n"
        "📌 16 уроков по словарному запасу\n"
        "📌 8 уроков грамматики\n"
        "📌 Видео-разборы корейских песен\n"
        "📌 Марафон по словам и разговорной практике\n"
        "📌 2 вебинара от Микки сонсенним (в живое время)\n"
        "📌 Обратная связь\n\n"
        "Количество мест: 5\n\n"
        "Цена: 24990 тенге/ 3990 ₽ в месяц\n\n"
        "Кто готов, нажимайте кнопку👇"
    )

async def send_fifth(message: Message):
    await message.answer(
        "Начнём сразу с самого полезного 🔥\n"
        "📅 Старт основной программы — 15 января.\n"
        "И уже 15го запускается марафон по пополнению словарного запаса.\n"
        "Мы не просто учим слова - мы учимся использовать их в речи.\n"
        "Также начнем с козырей правильного произношения😎 Идеальное комбо\n"
        "Правильное произношение + словарный запас",
        reply_markup=fifth_message_kb,
    )

async def send_sixth(message: Message):
    await message.answer(
        "Еще один шаг и ты студент KOREAN MINIMAL\n"
        "За 2 месяца обучения получишь все мои методы изучения корейского за 10 лет изучения корейского. "
        "Благодаря которому сейчас владею 6 уровнем ТOPIK, работала переводчиком в нефтяной компании.\n\n"
        "Главный результат:\n"
        "Полюбить логичный корейский язык\n"
        "Пройти 1 уровень и увидеть результат\n"
        "Цена: 12990 тенге / 1990 ₽",
        reply_markup=sixth_message_kb,
    )

# ================== ХЕНДЛЕРЫ ==================
@router.message(CommandStart())
async def start(message: Message):
    await send_first(message)

@router.callback_query(F.data == "start_course")
async def start_course(callback: CallbackQuery):
    await callback.answer()
    await send_second(callback.message)
    await send_third(callback.message)
    await send_fourth(callback.message)
    await send_fifth(callback.message)
    await send_sixth(callback.message)

# ================== WEB ==================
async def health(request: web.Request):
    return web.Response(text="OK")

async def main():
    app = web.Application()
    app.router.add_get("/", health)
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", int(os.environ.get("PORT", 8080))).start()

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
