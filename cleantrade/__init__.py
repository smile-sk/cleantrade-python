"""CleanTrade — non-custodial USDT (TRC20) payment API client.

Payments go straight to your wallet. No middlemen, no percentage fees,
no KYC. Just unique amounts + webhooks.

Quick start::

    from cleantrade import Client

    client = Client("sp_live_YOUR_KEY")
    order = client.create_order("indicator.zip", webhook_url="https://my.site/hook")
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
from .webhook import parse_webhook, WebhookPayload

__version__ = "0.1.0"
__all__ = [
    "Client",
    "Order",
    "parse_webhook",
    "WebhookPayload",
    "CleanTradeError",
    "UnauthorizedError",
    "LimitReachedError",
    "NotFoundError",
    "ConflictError",
    "BadRequestError",
    "__version__",
]
