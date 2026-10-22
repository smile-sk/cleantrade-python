"""CleanTrade API client (sync, built on requests).

Reference implementation of the endpoints at https://pay.cleantrade.info/docs
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

import requests

from .errors import CleanTradeError, error_from_response

DEFAULT_BASE_URL = "https://pay.cleantrade.info"
TIMEOUT_SECONDS = 15


@dataclass
class Order:
    """A payment order returned by the API.

    Show ``amount`` and ``wallet`` to the buyer. When the buyer sends the
    exact amount in USDT (TRC20), the status flips to ``paid`` and a webhook
    (if configured) fires with the ``tx_id``.
    """

    order_id: str
    amount: float
    wallet: str
    status: str
    product_id: str = ""
    created_at: str = ""
    tx_id: Optional[str] = None
    paid_at: Optional[str] = None
    webhook_url: str = ""
    customer_ref: str = ""
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: dict) -> "Order":
        return cls(
            order_id=data.get("order_id") or data.get("id", ""),
            amount=float(data.get("amount", 0)),
            wallet=data.get("wallet", ""),
            status=data.get("status", ""),
            product_id=data.get("product_id", ""),
            created_at=data.get("created_at", ""),
            tx_id=data.get("tx_id"),
            paid_at=data.get("paid_at"),
            webhook_url=data.get("webhook_url", ""),
            customer_ref=data.get("customer_ref", ""),
            raw=data,
        )

    @property
    def is_paid(self) -> bool:
        return self.status == "paid"

    @property
    def is_expired(self) -> bool:
        return self.status == "expired"


class Client:
    """Minimal, typed client for the CleanTrade Payment API.

    Usage::

        client = Client("sp_live_YOUR_KEY")
        order = client.create_order(product_id="indicator.zip",
                                    webhook_url="https://my.site/hook")
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: int = TIMEOUT_SECONDS,
        session: Optional[requests.Session] = None,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = session or requests.Session()
        self._session.headers.update(
            {"X-API-Key": api_key, "Content-Type": "application/json"}
        )

    # ------------------------------------------------------------------ #
    # Orders
    # ------------------------------------------------------------------ #
    def create_order(
        self,
        product_id: str,
        wallet: str,
        amount: Optional[float] = None,
        webhook_url: Optional[str] = None,
        customer_ref: Optional[str] = None,
    ) -> Order:
        """Create a payment order.

        :param product_id: your product identifier (shown in webhooks).
        :param wallet: YOUR TRC20 address (34 chars, starts with ``T``).
            Required: the buyer pays to this address, and orders are matched
            by the unique amount *within* this wallet. Pass it in every order
            — the same address or a different one, both are fine.
        :param amount: fixed amount. If omitted, CleanTrade generates a
            *unique* amount (e.g. 9.57) for that wallet. Prefer omitting it.
        :param webhook_url: URL CleanTrade POSTs to when the order is paid.
        :param customer_ref: your buyer id (Telegram id, email, ...).
        :raises BadRequestError: wallet is not a valid TRC20 address (HTTP 422).
        :raises ConflictError: this wallet already has an active order with
            this amount (HTTP 409).
        :raises LimitReachedError: monthly plan limit exceeded (HTTP 402).
        """
        payload: dict[str, Any] = {"product_id": product_id, "wallet": wallet}
        if amount is not None:
            payload["amount"] = amount
        if webhook_url:
            payload["webhook_url"] = webhook_url
        if customer_ref:
            payload["customer_ref"] = customer_ref
        data = self._request("POST", "/v1/orders", json=payload)
        return Order.from_dict(data)

    def get_order(self, order_id: str) -> Order:
        """Fetch the current status of an order."""
        data = self._request("GET", f"/v1/orders/{order_id}")
        return Order.from_dict(data)

    # ------------------------------------------------------------------ #
    # Subscription / billing
    # ------------------------------------------------------------------ #
    def subscribe(
        self,
        plan: str,
        customer_ref: str,
        webhook_url: Optional[str] = None,
    ) -> dict:
        """Subscribe to a plan; returns a plan payment order.

        Plans: ``free``, ``starter``, ``pro``, ``business``. After the
        plan order is paid, the webhook (or ``GET /v1/orders/{order_id}``)
        delivers your new ``api_key``.
        """
        payload: dict[str, Any] = {"plan": plan, "customer_ref": customer_ref}
        if webhook_url:
            payload["webhook_url"] = webhook_url
        return self._request("POST", "/v1/subscribe", json=payload)

    def me(self) -> dict:
        """Info about the current API key: plan, monthly limit, usage."""
        return self._request("GET", "/v1/subscribers/me")

    # ------------------------------------------------------------------ #
    # Misc
    # ------------------------------------------------------------------ #
    def health(self) -> dict:
        """Server health check (no API key needed)."""
        return self._request("GET", "/healthz")

    # ------------------------------------------------------------------ #
    # Internals
    # ------------------------------------------------------------------ #
    def _request(self, method: str, path: str, **kwargs) -> dict:
        url = self.base_url + path
        try:
            resp = self._session.request(method, url, timeout=self.timeout, **kwargs)
        except requests.RequestException as exc:
            raise CleanTradeError(f"network error: {exc}") from exc

        if 200 <= resp.status_code < 300:
            if resp.status_code == 204 or not resp.content:
                return {}
            try:
                return resp.json()
            except ValueError:
                raise CleanTradeError(f"invalid JSON from server (HTTP {resp.status_code})")

        detail = ""
        try:
            body = resp.json()
            detail = body.get("detail", "") if isinstance(body, dict) else ""
        except ValueError:
            detail = resp.text[:300]
        raise error_from_response(resp.status_code, detail)
