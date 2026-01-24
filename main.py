import asyncio
import os
import logging

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ================== ЛОГИРОВАНИЕ ==================
logging.basicConfig(level=logging.INFO)

# ================== ТОКЕН ==================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise SystemExit("❌ Установите переменную окружения BOT_TOKEN")

# ================== ЦЕНЫ (поменяй на свои) ==================
PRICE_STANDARD = "9 990₸"
PRICE_VIP = "14 990₸"

MASK = "░░░░░░░░░░░░░░"

# ключ: (chat_id, message_id) -> {"standard": bool, "vip": bool}
PRICE_STATE = {}

def build_text(show_standard: bool, show_vip: bool) -> str:
    standard_price = PRICE_STANDARD if show_standard else MASK
    vip_price = PRICE_VIP if show_vip else MASK

    return (
        "Тариф “стандарт” включает:\n"
        "📌 Большие выпуски о методах и\n"
        "правильном чтении\n"
        "📌 16 уроков по словарному запасу\n"
        "📌 8 уроков грамматики\n"
        "📌 Видео-разборы корейских песен\n"
        "📌 Марафон по словам и разговорной\n"
        "практике\n"
        "📌 Обратная связь\n\n"
        f"Цена: {standard_price}\n\n"
        "Тариф “VIP” включает:\n"
        "📌 Большие выпуски о методах и\n"
        "правильном чтении\n"
        "📌 16 уроков по словарному запасу\n"
        "📌 8 уроков грамматики\n"
        "📌 Видео-разборы корейских песен\n"
        "📌 Марафон по словам и разговорной\n"
        "практике\n"
        "📌 2 вебинара от Микки сонсенним (в\n"
        "живое время)\n"
        "📌 Обратная связь\n\n"
        "Количество мест: 5\n"
        f"Цена: {vip_price}\n"
        "Кто готов, нажимайте кнопку 👇"
    )

def build_kb(show_standard: bool, show_vip: bool):
    kb = InlineKeyboardBuilder()

    if show_standard:
        kb.button(text="✅ Цена «стандарт» показана", callback_data="price:noop")
    else:
        kb.button(text="💳 Показать цену «стандарт»", callback_data="price:standard")

    if show_vip:
        kb.button(text="✅ Цена «VIP» показана", callback_data="price:noop")
    else:
        kb.button(text="💎 Показать цену «VIP»", callback_data="price:vip")

    kb.adjust(1, 1)
    return kb.as_markup()

router = Router()

@router.message(CommandStart())
async def start(message: Message):
    sent = await message.answer(
        build_text(False, False),
        reply_markup=build_kb(False, False)
    )
    PRICE_STATE[(sent.chat.id, sent.message_id)] = {"standard": False, "vip": False}

@router.callback_query(F.data.startswith("price:"))
async def prices(callback: CallbackQuery):
    action = callback.data.split(":", 1)[1]

    if action == "noop":
        await callback.answer()
        return

    key = (callback.message.chat.id, callback.message.message_id)
    state = PRICE_STATE.get(key, {"standard": False, "vip": False})

    if action == "standard":
        state["standard"] = True
    elif action == "vip":
        state["vip"] = True

    PRICE_STATE[key] = state

    await callback.message.edit_text(
        build_text(state["standard"], state["vip"]),
        reply_markup=build_kb(state["standard"], state["vip"])
    )
    await callback.answer()

async def main():
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
