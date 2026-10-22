"""CleanTrade — USDT (TRC20) payment API client.

The buyer pays to YOUR TRC20 address, which you pass in every order. No
percentage fees, no KYC. Just unique amounts + webhooks.

Quick start::

    from cleantrade import Client

    client = Client("sp_live_YOUR_KEY")
    order = client.create_order("indicator.zip", "TYourTRC20Wallet...",
                                webhook_url="https://my.site/hook")
    print("Ask the buyer to send", order.amount, "USDT to", order.wallet)
"""

from .client import Client, Order
from .errors import (
    BadRequestError,
    CleanTradeError,
    ConflictError,
    LimitReachedError,
    NotFoundError,
    UnauthorizedError,
)
from .webhook import (make_fastapi_handler, parse_webhook, verify_webhook,
                      WebhookPayload)

__version__ = "0.1.2"
__all__ = [
    "Client",
    "Order",
    "parse_webhook",
    "verify_webhook",
    "WebhookPayload",
    "make_fastapi_handler",
    "CleanTradeError",
    "UnauthorizedError",
    "LimitReachedError",
    "NotFoundError",
    "ConflictError",
    "BadRequestError",
    "__version__",
]
