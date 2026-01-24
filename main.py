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

# ================== ЛОГИРОВАНИЕ ==================
logging.basicConfig(level=logging.INFO)

# ================== ТОКЕН ==================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    logging.error("⚠️ BOT_TOKEN не найден!")
    raise SystemExit("❌ Установите переменную окружения BOT_TOKEN")

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

# ================== BOT ==================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# ================== ГЛОБАЛЬНЫЕ ДАННЫЕ ==================
user_chain_tasks: dict[int, asyncio.Task] = {}

# Храним id сообщения 4 для каждого пользователя, чтобы редактировать его
user_fourth_msg_id: dict[int, int] = {}

# ================== 4 СООБЩЕНИЕ (ТЕКСТ НЕ МЕНЯЕМ) ==================
MASK = "░░░░░░░░░░░░░░░░░░░░░░░░"

PRICE_STANDARD = "12990 тенге/ 1990 ₽ в месяц"
PRICE_VIP = "24990 тенге/ 3990 ₽ в месяц"

# Состояние для 4-го сообщения (цены остаются после нажатия)
# key: chat_id -> {"standard": bool, "vip": bool}
fourth_prices_state: dict[int, dict[str, bool]] = {}


def build_fourth_text(show_standard: bool, show_vip: bool) -> str:
    standard_price_line = PRICE_STANDARD if show_standard else MASK
    vip_price_line = PRICE_VIP if show_vip else MASK

    return (
        "А все что в календаре, что ждёт тебя на курсе Система KOREAN MINIMAL 👇\n\n"
        "На курсе за месяц ты:\n\n"
        "▫️научишься быстро и правильно читать;\n"
        "▫️начнёшь красиво писать и понимать логику языка;\n"
        "▫️создашь личный план изучения корейского, который реально работает;\n"
        "▫️начнёшь говорить на корейском уже в процессе обучения.\n\n"
        "Курс состоит из 4 модулей:\n"
        "🔹 Модуль 1 — Чтение\n"
        "Освоение ассимиляции и произношения.\n"
        "🔹 Модуль 2 — Словарный запас (300 слов)\n"
        "Методы, практика, использование в диалогах.\n"
        "🔹 Модуль 3 — Говорить без страха\n"
        "Построение фраз, уверенная речь.\n"
        "🔹 Модуль 4 — Скорочтение\n"
        "Быстрое понимание текста и развитие скорости чтения.\n\n"
        "Тариф “стандарт” включает:\n"
        "📌 Большие выпуски о методах и правильном чтении\n"
        "📌 16 уроков по словарному запасу\n"
        "📌 8 уроков грамматики\n"
        "📌 Видео-разборы корейских песен\n"
        "📌 Марафон по словам и разговорной практике\n"
        "📌 Обратная связь \n\n"
        f"Цена: {standard_price_line}\n\n"
        "Тариф “VIP” включает:\n"
        "📌 Большие выпуски о методах и правильном чтении\n"
        "📌 16 уроков по словарному запасу\n"
        "📌 8 уроков грамматики\n"
        "📌 Видео-разборы корейских песен\n"
        "📌 Марафон по словам и разговорной практике\n"
        "📌 2 вебинара от Микки сонсенним (в живое время)\n"
        "📌 Обратная связь\n\n"
        "Количество мест: 5\n"
        f"Цена: {vip_price_line}\n\n"
        "Кто готов, нажимайте кнопку 👇"
    )


def build_fourth_kb(show_standard: bool, show_vip: bool) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text="💳 Оформить тариф «Стандарт»", url="https://web.tribute.tg/s/K0H")],
        [InlineKeyboardButton(text="💎 Оформить тариф «VIP»", url="https://t.me/minimalkor")],
    ]

    # "штрих" стандарт (показываем только пока цена скрыта)
    if not show_standard:
        rows.append([InlineKeyboardButton(text="░░░░░░░░░░░░", callback_data="show_price_standard")])

    # "штрих" VIP (показываем только пока цена скрыта)
    if not show_vip:
        rows.append([InlineKeyboardButton(text="░░░░░░░░░░░░", callback_data="show_price_vip")])

    rows.append([InlineKeyboardButton(text="📌 Подписаться на канал", url="https://t.me/minimalkorean")])

    return InlineKeyboardMarkup(inline_keyboard=rows)

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
    if PDF_PATH and os.path.exists(PDF_PATH):
        await message.answer_document(FSInputFile(PDF_PATH))
    else:
        await message.answer("⚠️ PDF не найден")


# ================== 4 СООБЩЕНИЕ (С ЦЕНОЙ ПО "ШТРИХУ") ==================
async def send_fourth(message: Message):
    # стартовое состояние: обе цены скрыты
    fourth_prices_state[message.chat.id] = {"standard": False, "vip": False}

    sent = await message.answer(
        build_fourth_text(False, False),
        reply_markup=build_fourth_kb(False, False)
    )
    user_fourth_msg_id[message.chat.id] = sent.message_id


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

# ================== ЦЕПОЧКА ==================
def start_chain(user_id: int, message: Message):
    old_task = user_chain_tasks.get(user_id)
    if old_task and not old_task.done():
        old_task.cancel()

    async def chain():
        try:
            await asyncio.sleep(5 * 60)
            await send_third(message)

            await asyncio.sleep(5 * 60)
            await send_fourth(message)

            await asyncio.sleep(3 * 60 * 60 - 10 * 60)
            await send_fifth(message)

            await asyncio.sleep(3 * 24 * 60 * 60)
            await send_sixth(message)

        except asyncio.CancelledError:
            logging.info(f"[{user_id}] Цепочка отменена")

    user_chain_tasks[user_id] = asyncio.create_task(chain())

# ================== ХЕНДЛЕРЫ ==================
@router.message(CommandStart())
async def start(message: Message):
    await send_first(message)


@router.callback_query(F.data == "start_course")
async def start_course(callback: CallbackQuery):
    await callback.answer()
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    await send_second(callback.message)
    start_chain(callback.from_user.id, callback.message)


# Нажал на "штрих" стандарт → раскрываем стандарт (штрих стандарта исчезнет, VIP штрих останется)
@router.callback_query(F.data == "show_price_standard")
async def show_price_standard(callback: CallbackQuery):
    await callback.answer()
    chat_id = callback.message.chat.id
    msg_id = user_fourth_msg_id.get(chat_id, callback.message.message_id)

    state = fourth_prices_state.get(chat_id, {"standard": False, "vip": False})
    state["standard"] = True
    fourth_prices_state[chat_id] = state

    new_text = build_fourth_text(state["standard"], state["vip"])
    new_kb = build_fourth_kb(state["standard"], state["vip"])

    await bot.edit_message_text(
        chat_id=chat_id,
        message_id=msg_id,
        text=new_text,
        reply_markup=new_kb,
    )


# Нажал на "штрих" VIP → раскрываем VIP (штрих VIP исчезнет, стандарт штрих останется если не был показан)
@router.callback_query(F.data == "show_price_vip")
async def show_price_vip(callback: CallbackQuery):
    await callback.answer()
    chat_id = callback.message.chat.id
    msg_id = user_fourth_msg_id.get(chat_id, callback.message.message_id)

    state = fourth_prices_state.get(chat_id, {"standard": False, "vip": False})
    state["vip"] = True
    fourth_prices_state[chat_id] = state

    new_text = build_fourth_text(state["standard"], state["vip"])
    new_kb = build_fourth_kb(state["standard"], state["vip"])

    await bot.edit_message_text(
        chat_id=chat_id,
        message_id=msg_id,
        text=new_text,
        reply_markup=new_kb,
    )


# ================== WEB (Railway) ==================
async def health(request: web.Request):
    return web.Response(text="Bot is running!")


async def start_web_server():
    app = web.Application()
    app.router.add_get("/", health)
    port = int(os.environ.get("PORT", "8080"))
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", port).start()


# ================== ЗАПУСК ==================
async def main():
    await start_web_server()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
