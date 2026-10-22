"""Webhook receiver example (FastAPI).

CleanTrade POSTs to your webhook_url when an order is paid, retrying up to
5 times until your server answers 2xx. This server auto-delivers the goods.

Run:
    pip install fastapi uvicorn cleantrade
    uvicorn webhook_server:app --port 8081

Expose it to the internet (e.g. via a reverse proxy or tunnel) and pass the
public URL when creating orders::

    client.create_order("indicator.zip", "TYourTRC20Wallet...",
                        webhook_url="https://your.domain/hook")
"""

from fastapi import FastAPI, Request

from cleantrade import make_fastapi_handler, WebhookPayload

app = FastAPI(title="CleanTrade webhook receiver")

# In-memory store: order_id -> product (file path, license key, access ...)
GOODS = {
    "indicator.zip": "https://dl.example.com/indicator.zip",
}


def deliver(p: WebhookPayload) -> None:
    """Your business logic: unlock the purchase for the buyer."""
    if not p.is_paid:
        return
    product = GOODS.get(p.product_id)
    print(f"[PAID] order={p.order_id} product={p.product_id} tx={p.tx_id} "
          f"amount={p.amount} -> deliver {product}")
    # Send the download link / key to the buyer here (Telegram, email, ...).
    # Use p.customer_ref to identify the buyer.


@app.post("/hook")
async def hook(request: Request) -> str:
    return make_fastapi_handler(deliver)(await request.body())


@app.get("/healthz")
async def healthz() -> dict:
    return {"ok": True}
