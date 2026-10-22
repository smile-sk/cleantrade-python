"""Signature verification: the documented HMAC actually validates.

CleanTrade signs every webhook as HMAC-SHA256 over "<timestamp>.<raw body>"
and sends X-CleanTrade-Timestamp / X-CleanTrade-Signature. If this drifts,
every integrator who follows the README silently starts accepting forgeries.

Run:  python -m unittest tests.test_webhook -v
"""

import hashlib
import hmac
import json
import time
import unittest

from cleantrade import verify_webhook

SECRET = "whsec_test_123"


def sign(body: bytes, timestamp: str, secret: str = SECRET) -> str:
    return "sha256=" + hmac.new(
        secret.encode("utf-8"),
        timestamp.encode("ascii") + b"." + body,
        hashlib.sha256,
    ).hexdigest()


class TestVerifyWebhook(unittest.TestCase):
    def setUp(self):
        self.payload = {"order_id": "o1", "status": "paid", "amount": 9.57,
                        "tx_id": "t1", "product_id": "plan:starter"}
        self.body = json.dumps(self.payload, ensure_ascii=False,
                               sort_keys=True, separators=(",", ":")).encode()
        self.ts = str(int(time.time()))

    def test_valid_signature(self):
        sig = sign(self.body, self.ts)
        self.assertTrue(verify_webhook(self.body, sig, self.ts, SECRET))

    def test_wrong_secret_rejected(self):
        sig = sign(self.body, self.ts, "other_secret")
        self.assertFalse(verify_webhook(self.body, sig, self.ts, SECRET))

    def test_tampered_body_rejected(self):
        sig = sign(self.body, self.ts)
        tampered = self.body.replace(b"9.57", b"0.01")
        self.assertFalse(verify_webhook(tampered, sig, self.ts, SECRET))

    def test_replay_rejected(self):
        old = str(int(time.time()) - 3600)
        sig = sign(self.body, old)
        self.assertFalse(verify_webhook(self.body, sig, old, SECRET))

    def test_replay_allowed_inside_tolerance(self):
        recent = str(int(time.time()) - 60)
        sig = sign(self.body, recent)
        self.assertTrue(verify_webhook(self.body, sig, recent, SECRET))

    def test_missing_pieces_rejected(self):
        self.assertFalse(verify_webhook(self.body, "", self.ts, SECRET))
        self.assertFalse(verify_webhook(self.body, "sha256=x", "", SECRET))
        self.assertFalse(verify_webhook(self.body, "sha256=x", self.ts, ""))
        self.assertFalse(verify_webhook(self.body, "sha256=x", "not-a-ts", SECRET))


if __name__ == "__main__":
    unittest.main()
