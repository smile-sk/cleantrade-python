"""Telegram bot that sells a digital product for USDT (TRC20) via CleanTrade.

Pattern: create order -> show unique amount + wallet -> poll until paid ->
deliver the goods. No webhook server needed (works behind NAT).

Setup:
    pip install aiogram cleantrade
    export TELEGRAM_BOT_TOKEN=...            # from @BotFather
    export CLEANTRADE_API_KEY=sp_live_...    # from pay.cleantrade.info

Run:
    python bot.py
"""

import asyncio
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from cleantrade import Client, Order

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
API_KEY = os.environ["CLEANTRADE_API_KEY"]

PRODUCT_ID = "indicator.zip"
PRICE_TEXT = "9.99 USDT"          # display price (the actual unique amount differs)
DOWNLOAD_LINK = "https://dl.example.com/indicator.zip"

bot = Bot(BOT_TOKEN)
dp = Dispatcher()
client = Client(API_KEY)

# order_id -> chat_id, so the polling task knows who to deliver to
active: dict[str, int] = {}


@dp.message(CommandStart())
async def start(message: Message) -> None:
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Buy indicator — 9.99 USDT")]],
        resize_keyboard=True,
    )
    await message.answer(
        "Hi! I sell the SuperIndicator for USDT (TRC20).\n"
        "No registration, no KYC — you send crypto straight to my wallet\n"
        "and the bot detects it in ~30 seconds.",
        reply_markup=kb,
    )


@dp.message(F.text == "Buy indicator — 9.99 USDT")
async def buy(message: Message) -> None:
    order = client.create_order(
        product_id=PRODUCT_ID,
        customer_ref=str(message.from_user.id),
    )
    active[order.order_id] = message.chat.id
    await message.answer(
        f"Send **exactly {order.amount} USDT** (TRC20) to:\n\n"
        f"`{order.wallet}`\n\n"
        f"⚠️ Send the exact amount — the payment is matched by it.\n"
        f"⏳ Detection takes ~30 seconds. I'll notify you here.",
        parse_mode="Markdown",
    )
    asyncio.create_task(wait_for_payment(order))


async def wait_for_payment(order: Order) -> None:
    try:
        while True:
            order = client.get_order(order.order_id)
            if order.is_paid:
                await bot.send_message(
                    active[order.order_id],
                    f"✅ Payment confirmed! tx: `{order.tx_id}`\n"
                    f"Your file: {DOWNLOAD_LINK}",
                    parse_mode="Markdown",
                )
                return
            if order.is_expired:
                await bot.send_message(
                    active[order.order_id],
                    "⏰ The order expired (24h window). Press the button to create a new one.",
                )
                return
            await asyncio.sleep(5)
    finally:
        active.pop(order.order_id, None)


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
