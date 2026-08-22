"""Tiny tests for the SDK — no external test deps (uses unittest).

Run:  python -m unittest tests.test_client -v
"""

import unittest
from unittest import mock

import requests

from cleantrade import (
    Client,
    Order,
    parse_webhook,
    UnauthorizedError,
    LimitReachedError,
    NotFoundError,
)


class TestOrder(unittest.TestCase):
    def test_from_dict(self):
        o = Order.from_dict({
            "order_id": "abc123", "product_id": "x", "amount": 9.57,
            "wallet": "T...", "status": "created", "created_at": "now",
        })
        self.assertEqual(o.amount, 9.57)
        self.assertFalse(o.is_paid)

    def test_paid(self):
        o = Order.from_dict({"order_id": "a", "amount": 1, "wallet": "T",
                             "status": "paid", "tx_id": "tx1"})
        self.assertTrue(o.is_paid)
        self.assertEqual(o.tx_id, "tx1")


class TestClient(unittest.TestCase):
    def _client(self, resp):
        session = mock.Mock(spec=requests.Session)
        session.headers = {"X-API-Key": "sp_live_x", "Content-Type": "application/json"}
        session.request.return_value = resp
        return Client("sp_live_x", session=session), session

    def test_create_order_payload(self):
        resp = mock.Mock(status_code=201)
        resp.json.return_value = {"order_id": "abc", "amount": 9.57,
                                  "wallet": "T", "status": "created"}
        client, session = self._client(resp)
        order = client.create_order("indicator.zip", webhook_url="https://h/x")
        self.assertEqual(order.order_id, "abc")
        _, kwargs = session.request.call_args
        payload = kwargs["json"]
        self.assertEqual(payload["product_id"], "indicator.zip")
        self.assertEqual(payload["webhook_url"], "https://h/x")
        self.assertNotIn("amount", payload)  # unique amount by default
        self.assertEqual(session.headers["X-API-Key"], "sp_live_x")

    def test_error_mapping(self):
        resp = mock.Mock(status_code=401)
        resp.json.return_value = {"detail": "invalid api key"}
        client, _ = self._client(resp)
        with self.assertRaises(UnauthorizedError):
            client.get_order("abc")

        resp = mock.Mock(status_code=402)
        resp.json.return_value = {"detail": "monthly order limit reached"}
        client, _ = self._client(resp)
        with self.assertRaises(LimitReachedError):
            client.create_order("x")

        resp = mock.Mock(status_code=404)
        resp.json.return_value = {"detail": "order not found"}
        client, _ = self._client(resp)
        with self.assertRaises(NotFoundError):
            client.get_order("nope")


class TestWebhook(unittest.TestCase):
    def test_parse(self):
        p = parse_webhook(b'{"order_id": "abc", "status": "paid", "amount": 9.57, "tx_id": "t1"}')
        self.assertIsNotNone(p)
        assert p is not None
        self.assertTrue(p.is_paid)
        self.assertEqual(p.tx_id, "t1")

    def test_plan_webhook_has_key(self):
        p = parse_webhook({"order_id": "abc", "status": "paid", "amount": 29.99,
                           "plan": "pro", "api_key": "sp_live_new"})
        assert p is not None
        self.assertEqual(p.api_key, "sp_live_new")

    def test_garbage(self):
        self.assertIsNone(parse_webhook(b"not json"))
        self.assertIsNone(parse_webhook(b"{}"))


if __name__ == "__main__":
    unittest.main()
