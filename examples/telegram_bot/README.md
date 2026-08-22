# Telegram Subscription Bot — Python (aiogram + CleanTrade API)

A ready-to-run Telegram bot that sells a digital product for **USDT (TRC20)**
with zero middlemen: the money goes straight to *your* wallet, CleanTrade
only detects the payment and tells the bot.

## How it works

1. Buyer presses the button.
2. Bot creates an order via CleanTrade API → gets a **unique amount** (e.g. `9.57 USDT`).
3. Bot shows the amount + your wallet address.
4. Buyer sends USDT directly to your wallet.
5. CleanTrade detects the on-chain payment in ~30 seconds.
6. Bot delivers the download link automatically.

No KYC, no approval queue, no 1–3% cut. Just a flat subscription.

## Run

```bash
pip install -r requirements.txt
export TELEGRAM_BOT_TOKEN=123456:ABC...     # from @BotFather
export CLEANTRADE_API_KEY=sp_live_...       # from pay.cleantrade.info
python bot.py
```

## Files

- `bot.py` — the whole bot (~100 lines, polling-based, works behind NAT).
- `requirements.txt` — aiogram + cleantrade.

## Going further

- Want **instant** delivery? Replace polling with a webhook receiver
  (`../webhook_server.py`) and pass `webhook_url` to `create_order()`.
- Want to sell multiple products? Map `product_id` → price/button in `bot.py`.
