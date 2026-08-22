"""Minimal example: create an order and poll until it is paid.

    CLEANTRADE_API_KEY=sp_live_... python poll_status.py

The "polling" pattern is the simplest one — no public URL needed.
For production prefer webhooks (see webhook_server.py).
"""

import os
import time

from cleantrade import Client

client = Client(os.environ["CLEANTRADE_API_KEY"])

# 1. Create an order — the API returns a unique amount and YOUR wallet.
order = client.create_order(
    product_id="indicator.zip",
    customer_ref="user123",
    # webhook_url="https://my.site/hook",  # optional
)
print(f"Ask the buyer to send exactly {order.amount} USDT (TRC20) to {order.wallet}")

# 2. Poll until paid (or expired).
while True:
    order = client.get_order(order.order_id)
    if order.is_paid:
        print(f"PAID! tx_id={order.tx_id} — deliver the goods now.")
        break
    if order.is_expired:
        print("Order expired (24h window). Create a new one.")
        break
    time.sleep(5)
