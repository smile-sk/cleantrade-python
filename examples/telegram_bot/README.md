# Telegram Subscription Bot — Python (aiogram + CleanTrade API)

A ready-to-run Telegram bot that sells a digital product for **USDT (TRC20)**
on a flat subscription: the buyer pays to *your own* TRC20 wallet (the bot passes
it in every order), and CleanTrade detects the payment and tells the bot.

## How it works

1. Buyer presses the button.
2. Bot creates an order via CleanTrade API → gets a **unique amount** (e.g. `9.57 USDT`).
3. Bot shows the amount + your wallet address from the order.
4. Buyer sends USDT to that address.
5. CleanTrade detects the on-chain payment, usually under a minute.
6. Bot delivers the download link automatically.

No KYC, no approval queue, no per-transaction cut. Just a flat subscription.

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
