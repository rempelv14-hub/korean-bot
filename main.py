import asyncio
import os
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from flask import Flask

# ================== ЛОГИРОВАНИЕ ==================
logging.basicConfig(level=logging.INFO)

# ================== ТОКЕН ==================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    logging.error("⚠️ BOT_TOKEN не найден! Проверь Worker Variables на Railway.")
    raise SystemExit("❌ Установите переменную окружения BOT_TOKEN в Railway")

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

# 4-е сообщение — 3 кнопки
fourth_message_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Оформить тариф «стандарт»", url="https://web.tribute.tg/s/K0H")],
        [InlineKeyboardButton(text="Оформить тариф «VIP»", url="https://t.me/minimalkor")],
        [InlineKeyboardButton(text="Подписаться на канал", url="https://t.me/minimalkorean")]
    ]
)

# 5-е сообщение — 2 кнопки
fifth_message_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Оплатить «Стандарт»", url="https://web.tribute.tg/s/K0H")],
        [InlineKeyboardButton(text="Оплатить «VIP»", url="https://t.me/minimalkor")]
    ]
)

# 6-е сообщение — 1 кнопка (подписка)
subscription_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Оформить подписку", url="https://t.me/tribute/app?startapp=sK0H")]
    ]
)

# ================== BOT ==================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# ================== ГЛОБАЛЬНЫЕ ДАННЫЕ ==================
active_users = {}  # user_id -> {"paid": bool, "tasks": [asyncio_task]}

# ================== СООБЩЕНИЯ ==================
async def send_video(message: Message):
    await message.answer(
        "Отлично! Начнём с подарка 🎁\n"
        "Я подготовила видео о том, как правильно планировать изучение корейского,\n"
        "чтобы не бросить через неделю и не тратить время впустую.\n\n"
        f"👉 Смотри видео: {VIDEO_URL}\n"
        "После просмотра тебя ждёт ещё один бонус ✨\n(я пришлю его чуть позже)"
    )

async def send_pdf(message: Message):
    await message.answer(
        "Как и обещала — вот твой бонус 📘✨\n"
        "Дарю календарь для изучения корейского.\n"
        "Он поможет дойти до 4го уровня системно и без срывов."
    )
    if PDF_PATH and os.path.exists(PDF_PATH):
        await message.answer_document(FSInputFile(PDF_PATH))
    else:
        await message.answer("⚠️ PDF не найден")

async def send_course_presentation(message: Message):
    await message.answer(
        "А все что в календаре, что ждёт тебя на курсе Система KOREAN MINIMAL 👇\n"
        "На курсе за месяц ты:\n"
        "• научишься быстро и правильно читать;\n"
        "• начнёшь красиво писать и понимать логику языка;\n"
        "• создашь личный план изучения корейского, который реально работает;\n"
        "• начнёшь говорить на корейском уже в процессе обучения.\n\n"
        "Курс состоит из 4 модулей:\n"
        "🔹 Модуль 1 — Чтение\nОсвоение ассимиляции и произношения.\n"
        "🔹 Модуль 2 — Словарный запас (300 слов)\nМетоды, практика, использование в диалогах.\n"
        "🔹 Модуль 3 — Говорить без страха\nПостроение фраз, уверенная речь.\n"
        "🔹 Модуль 4 — Скорочтение\nБыстрое понимание текста и развитие скорости чтения.\n\n"
        "Тариф “стандарт” включает:\n"
        "📌 Большие выпуски о методах и правильном чтении\n"
        "📌 16 уроков по словарному запасу\n"
        "📌 8 уроков грамматики\n"
        "📌 Видео-разборы корейских песен\n"
        "📌 Марафон по словам и разговорной практике\n"
        "📌 Обратная связь от ментора\n"
        "Цена: 12990 тенге / 1990 ₽ в месяц\n\n"
        "Тариф “VIP” включает:\n"
        "📌 Большие выпуски о методах и правильном чтении\n"
        "📌 16 уроков по словарному запасу\n"
        "📌 8 уроков грамматики\n"
        "📌 Видео-разборы корейских песен\n"
        "📌 Марафон по словам и разговорной практике\n"
        "📌 2 вебинара от Микки сонсенним\n"
        "📌 Обратная связь от Микки сонсенним\n"
        "Количество мест: 5\n"
        "Цена: 24990 тенге / 3990 ₽",
        reply_markup=fourth_message_kb
    )

async def send_useful_tips(message: Message):
    await message.answer(
        "Начнём сразу с самого полезного 🔥\n"
        "📅 Старт основной программы — 15 января.\n"
        "И уже 15го запускается марафон по пополнению словарного запаса.\n"
        "Мы не просто учим слова - мы учимся использовать их в речи.\n"
        "Также начнем с козырей - правильного произношения😎 "
        "Идеальное комбо = Правильное произношение + словарный запас",
        reply_markup=fifth_message_kb
    )

async def send_final_message(message: Message):
    await message.answer(
        "Еще один шаг и ты студент KOREAN MINIMAL\n"
        "За 2 месяца обучения получишь все мои методы изучения корейского за 10 лет изучения корейского. "
        "Благодаря которому сейчас владею 6 уровнем ТOPIK, работала переводчиком в нефтяной компании.\n\n"
        "Главный результат:\n"
        "Полюбить логичный корейский язык\n"
        "Пройти 1 уровень и увидеть результат\n"
        "Цена: 12990 тенге / 1990 ₽",
        reply_markup=subscription_kb
    )

# ================== ФУНКЦИЯ ЛОГИРОВАНИЯ ==================
async def send_with_logging(user_id: int, message: Message, send_func, msg_name: str):
    if not active_users[user_id]["paid"]:
        await send_func(message)
        logging.info(f"[{user_id}] Отправлено {msg_name} в {datetime.now().strftime('%H:%M:%S')}")

# ================== ЦЕПОЧКА СООБЩЕНИЙ ==================
def start_message_chain(user_id: int, message: Message):
    if user_id not in active_users:
        active_users[user_id] = {"paid": False, "tasks": []}

    async def chain():
        try:
            # 1-е сообщение — сразу
            await send_with_logging(user_id, message, send_video, "1-е сообщение (видео)")

            # 2-е сообщение — сразу после нажатия старт
            await send_with_logging(user_id, message, send_pdf, "2-е сообщение (PDF)")

            # 3-е сообщение — через 5 минут
            await asyncio.sleep(5 * 60)
            await send_with_logging(user_id, message, send_course_presentation, "3-е сообщение (презентация курса)")

            # 4-е сообщение — через 10 минут после старта
            await asyncio.sleep(5 * 60)
            await send_with_logging(user_id, message, send_useful_tips, "4-е сообщение (полезные советы)")

            # 5-е сообщение — через 3 часа после старта
            await asyncio.sleep(3 * 60 * 60 - 10 * 60)
            await send_with_logging(user_id, message, send_final_message, "5-е сообщение (финальное)")

            # 6-е сообщение — через 3 дня
            await asyncio.sleep(3 * 24 * 60 * 60)
            if not active_users[user_id]["paid"]:
                await message.answer(
                    "Напоминание: ещё есть бонусы и возможности подписки! 🚀",
                    reply_markup=subscription_kb
                )
                logging.info(f"[{user_id}] Отправлено 6-е сообщение (напоминание) в {datetime.now().strftime('%H:%M:%S')}")
        except asyncio.CancelledError:
            logging.info(f"[{user_id}] Цепочка сообщений отменена")
        finally:
            active_users[user_id]["tasks"] = []

    task = asyncio.create_task(chain())
    active_users[user_id]["tasks"].append(task)
    logging.info(f"[{user_id}] Запущена цепочка сообщений с таймингами")

# ================== ХЕНДЛЕРЫ ==================
@router.message(CommandStart())
async def start(message: Message):
    user_id = message.from_user.id
    if user_id not in active_users:
        active_users[user_id] = {"paid": False, "tasks": []}

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
        reply_markup=start_kb
    )

@router.callback_query(F.data == "start_course")
async def start_course(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in active_users:
        active_users[user_id] = {"paid": False, "tasks": []}

    await callback.answer()
    start_message_chain(user_id, callback.message)

# ================== ЗАПУСК ==================
async def start_bot():
    logging.info("Бот запущен")
    await dp.start_polling(bot)

# ================== FLASK ==================
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

if __name__ == "__main__":
    asyncio.run(start_bot())
