# CleanTrade — Python SDK

Accept **USDT (TRC20)** payments in your bot, microservice or small e-commerce
— **without a payment aggregator**. No middlemen, no percentage fees, no KYC,
no smart contracts. The money goes straight to **your** wallet.

```python
from cleantrade import Client

client = Client("sp_live_YOUR_KEY")
order = client.create_order("indicator.zip", webhook_url="https://my.site/hook")

print(f"Ask the buyer to send {order.amount} USDT to {order.wallet}")
# → Ask the buyer to send 9.57 USDT to TJ7...K9
```

That's it. The buyer sends the exact amount, CleanTrade detects the on-chain
payment in **~30 seconds** and fires a webhook with the `tx_id`. You deliver
the goods.

## Why CleanTrade

| | CleanTrade | Classic crypto gateways |
|---|---|---|
| Fee | **0%** — flat subscription | 1–3% of every payment |
| Funds | **Non-custodial** — direct to your wallet | Held by the gateway (custody) |
| KYC / approval | **None** — API key in ~60 seconds | Docs, business registration, review queue |
| Setup | `pip install cleantrade` | Weeks of integration |
| Detection | ~30 seconds (unique amounts) | Minutes to hours |

## Install

```bash
pip install cleantrade
```

Get your API key at [pay.cleantrade.info](https://pay.cleantrade.info)
(Free tier: $0/mo, 5 orders; yearly plans: 12 months for the price of 10).

## Quick start

### 1. Create an order (polling pattern)

```python
import time
from cleantrade import Client

client = Client("sp_live_YOUR_KEY")
order = client.create_order("indicator.zip", customer_ref="user123")

while True:
    order = client.get_order(order.order_id)
    if order.is_paid:
        print("Paid!", order.tx_id)      # deliver the goods
        break
    time.sleep(5)
```

### 2. Webhooks (recommended for production)

Pass a `webhook_url` when creating the order. CleanTrade POSTs to it on
payment and retries until your server answers 2xx.

```python
from cleantrade import parse_webhook

def handle(body: bytes):
    payload = parse_webhook(body)
    if payload and payload.is_paid:
        deliver(payload.product_id, payload.tx_id, payload.customer_ref)
    return "ok"
```

See [`examples/webhook_server.py`](examples/webhook_server.py) for a complete
FastAPI receiver, [`examples/express_webhook.js`](examples/express_webhook.js)
for a Node.js/Express receiver (`cd examples && npm install && node
express_webhook.js`), and [`examples/telegram_bot/`](examples/telegram_bot/) for
a ready-to-run Telegram shop bot.

## API reference

| Method | Path | Description |
|---|---|---|
| `POST` | `/v1/orders` | Create an order → unique amount + your wallet |
| `GET` | `/v1/orders/{order_id}` | Check order status |
| `POST` | `/v1/subscribe` | Subscribe to a plan (pays with USDT) |
| `GET` | `/v1/subscribers/me` | Current plan, limit, monthly usage |
| `GET` | `/healthz` | Health check |

Authentication: header `X-API-Key` (the SDK sets it for you).
Full spec: [Swagger UI](https://pay.cleantrade.info/docs) ·
[OpenAPI JSON](https://pay.cleantrade.info/openapi.json)

### Order statuses

- `created` — waiting for payment (valid 24h)
- `paid` — payment detected, `tx_id` available
- `expired` — the 24h window passed

### Errors (exceptions)

| HTTP | Exception | Meaning |
|---|---|---|
| 400 | `BadRequestError` | Invalid request (e.g. unknown plan) |
| 401 | `UnauthorizedError` | Missing / invalid API key |
| 402 | `LimitReachedError` | Monthly plan limit exceeded — upgrade |
| 404 | `NotFoundError` | Order not found |
| 409 | `ConflictError` | Amount busy / no free unique amounts right now |

## How payment detection works

Every order gets a **unique amount** (`9.57`, `9.84`, …). The buyer sends
exactly that amount to your wallet — no smart contract, no extra gas, no
address-per-order logic. CleanTrade polls the chain every ~30 seconds, matches
the amount and confirms the order.

## Plans

| Plan | Price | Orders/mo | Extras |
|---|---|---|---|
| Free | $0 | 5 | 1 wallet, webhooks with retries |
| Starter | $9.99 | 100 | 3 wallets, priority support |
| Pro | $29.99 | 3000 | Unlimited wallets, multiple API keys, webhook log |
| Business | $79.99 | Unlimited | Own domain, SLA, dedicated support |
| Starter Yearly | $99.90/yr | 100 | 12 months for the price of 10 |
| Pro Yearly | $299.90/yr | 3000 | 12 months for the price of 10 |
| Business Yearly | $799.90/yr | Unlimited | 12 months for the price of 10 |

No percentage — ever. [Compare plans](https://pay.cleantrade.info/subscribe.html)

## License

MIT
