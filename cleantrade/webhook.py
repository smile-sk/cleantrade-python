"""Helpers for receiving CleanTrade webhooks in your own server.

CleanTrade POSTs a JSON payload to your ``webhook_url`` when an order is
paid (retries on non-2xx responses). This module parses and validates it
so your handler stays tiny::

    from cleantrade import parse_webhook

    def handle(request):
        data = parse_webhook(request.body)      # dict | None
        if data and data["status"] == "paid":
            deliver(data["order_id"], data["tx_id"])
        return "ok"
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class WebhookPayload:
    """A validated webhook event."""

    order_id: str
    status: str
    amount: float
    product_id: str = ""
    tx_id: Optional[str] = None
    paid_at: Optional[str] = None
    customer_ref: str = ""
    plan: Optional[str] = None       # present for plan (subscription) orders
    api_key: Optional[str] = None    # present for plan orders after activation
    raw: dict = field(default_factory=dict, repr=False)

    @property
    def is_paid(self) -> bool:
        return self.status == "paid"


def parse_webhook(body: bytes | str | dict) -> Optional[WebhookPayload]:
    """Parse a webhook body into a :class:`WebhookPayload`.

    Returns ``None`` if the body is not valid JSON or misses ``order_id``.
    """
    try:
        data = json.loads(body) if isinstance(body, (bytes, str)) else body
    except (ValueError, TypeError):
        return None
    if not isinstance(data, dict) or not data.get("order_id"):
        return None
    try:
        amount = float(data.get("amount", 0))
    except (TypeError, ValueError):
        amount = 0.0
    return WebhookPayload(
        order_id=str(data["order_id"]),
        status=str(data.get("status", "")),
        amount=amount,
        product_id=str(data.get("product_id", "")),
        tx_id=data.get("tx_id"),
        paid_at=data.get("paid_at"),
        customer_ref=str(data.get("customer_ref", "")),
        plan=data.get("plan"),
        api_key=data.get("api_key"),
        raw=data,
    )


def make_fastapi_handler(deliver):
    """Adapter for FastAPI: wrap your ``deliver(payload)`` callable.

    Example::

        from cleantrade import parse_webhook, make_fastapi_handler

        app = FastAPI()

        def deliver(p: WebhookPayload):
            if p.is_paid:
                unlock_order(p.order_id, p.tx_id)

        @app.post("/hook")
        async def hook(request: Request):
            return make_fastapi_handler(deliver)(await request.body())
    """

    def handler(body: bytes):
        payload = parse_webhook(body)
        if payload is None:
            return "ok"  # nothing to do — don't trigger retries with an error
        deliver(payload)
        return "ok"

    return handler
