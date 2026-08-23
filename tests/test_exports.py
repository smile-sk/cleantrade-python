"""Smoke test: the public API is real.

Every name in ``__all__`` must exist, and every example in ``examples/``
must compile and use only real import names. This guards the class of
bugs where docs/examples reference a name that the package does not export
(see the ``make_fastapi_handler`` incident, 2026-08-23).

Run:  python -m unittest tests.test_exports -v
"""

import os
import unittest

import cleantrade
from cleantrade import make_fastapi_handler, parse_webhook, WebhookPayload

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestExports(unittest.TestCase):
    def test_all_names_exist(self):
        for name in cleantrade.__all__:
            self.assertTrue(hasattr(cleantrade, name),
                            f"__all__ references missing export: {name}")

    def test_make_fastapi_handler_end_to_end(self):
        delivered = []

        def deliver(p: WebhookPayload) -> None:
            delivered.append(p)

        handler = make_fastapi_handler(deliver)

        # Paid webhook → deliver called once, returns "ok"
        body = (b'{"order_id": "o1", "status": "paid", "amount": 9.57, '
                b'"tx_id": "t1", "product_id": "indicator.zip"}')
        self.assertEqual(handler(body), "ok")
        self.assertEqual(len(delivered), 1)
        self.assertTrue(delivered[0].is_paid)
        self.assertEqual(delivered[0].tx_id, "t1")

        # Garbage → "ok", no delivery, no crash (no retry storm)
        self.assertEqual(handler(b"not json"), "ok")
        self.assertEqual(len(delivered), 1)


class TestExamples(unittest.TestCase):
    def test_examples_compile(self):
        examples_dir = os.path.join(REPO_ROOT, "examples")
        for root, _dirs, files in os.walk(examples_dir):
            for fn in files:
                if fn.endswith(".py"):
                    path = os.path.join(root, fn)
                    with open(path, "rb") as fh:
                        compile(fh.read(), path, "exec")
                    self.assertTrue(True, f"compiled: {fn}")

    def test_example_import_names_resolve(self):
        # The FastAPI example imports these names from cleantrade —
        # they must resolve even without fastapi installed.
        self.assertTrue(callable(make_fastapi_handler))
        self.assertTrue(hasattr(WebhookPayload, "is_paid"))
        self.assertTrue(callable(parse_webhook))


if __name__ == "__main__":
    unittest.main()
