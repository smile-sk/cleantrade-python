/**
 * CleanTrade webhook receiver example (Node.js + Express).
 *
 * CleanTrade POSTs to your webhook_url when an order is paid, retrying up to
 * 5 times until your server answers 2xx. This server auto-delivers the goods.
 *
 * Requirements: Node.js 18+ (global fetch) and Express.
 *
 * Run:
 *   npm install express
 *   node express_webhook.js
 *
 * Expose it to the internet (e.g. via a reverse proxy or tunnel) and pass the
 * public URL when creating orders:
 *
 *   node -e "const {createOrder} = require('./express_webhook'); \
 *     createOrder('indicator.zip', 'https://your.domain/hook').then(console.log)"
 *
 * The printed order contains `amount` and `wallet` — show them to the buyer.
 */

const express = require("express");

const API_KEY = process.env.CLEANTRADE_API_KEY || "sp_live_YOUR_KEY";
const BASE_URL = process.env.CLEANTRADE_BASE_URL || "https://pay.cleantrade.info";

// In-memory store: product_id -> download URL (replace with your logic).
const GOODS = {
  "indicator.zip": "https://dl.example.com/indicator.zip",
};

// ---------------------------------------------------------------------------
// API client (minimal — mirrors the Python SDK's Client.create_order)
// ---------------------------------------------------------------------------

/**
 * Create a payment order.
 * @param {string} productId your product identifier (shown in webhooks)
 * @param {{amount?: number, webhookUrl?: string, customerRef?: string}} [opts]
 *   amount: fixed amount. If omitted, CleanTrade generates a *unique* amount
 *   (e.g. 9.57) so payments can be matched on-chain without smart contracts.
 *   Prefer omitting it.
 *   webhookUrl: URL CleanTrade POSTs to when the order is paid.
 *   customerRef: your buyer id (Telegram id, email, ...).
 * @returns {Promise<{order_id: string, amount: number, wallet: string, status: string, created_at: string}>}
 */
async function createOrder(productId, { amount, webhookUrl, customerRef } = {}) {
  const body = { product_id: productId };
  if (amount !== undefined) body.amount = amount;
  if (webhookUrl) body.webhook_url = webhookUrl;
  if (customerRef) body.customer_ref = customerRef;

  const resp = await fetch(`${BASE_URL}/v1/orders`, {
    method: "POST",
    headers: {
      "X-API-Key": API_KEY,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  if (!resp.ok) {
    const detail = await resp.text().catch(() => "");
    throw new Error(`CleanTrade API error ${resp.status}: ${detail}`);
  }
  return resp.json();
}

// ---------------------------------------------------------------------------
// Webhook receiver
// ---------------------------------------------------------------------------

/**
 * Your business logic: unlock the purchase for the buyer.
 * @param {{order_id: string, status: string, amount: number, product_id: string,
 *          tx_id?: string, paid_at?: string, customer_ref?: string}} payload
 */
function deliver(payload) {
  if (payload.status !== "paid") return;
  const product = GOODS[payload.product_id];
  console.log(
    `[PAID] order=${payload.order_id} product=${payload.product_id} ` +
      `tx=${payload.tx_id} amount=${payload.amount} -> deliver ${product}`
  );
  // Send the download link / key to the buyer here (Telegram, email, ...).
  // Use payload.customer_ref to identify the buyer.
}

const app = express();

// Raw body as text so we can mirror the Python parse_webhook behaviour:
// invalid JSON or a body without order_id => answer 2xx, never crash, and
// don't trigger CleanTrade retries with an error status.
app.use(express.text({ type: "*/*" }));

app.post("/hook", (req, res) => {
  let payload;
  try {
    payload = JSON.parse(req.body || "{}");
  } catch {
    return res.send("ok"); // not valid JSON — nothing to do
  }
  if (!payload.order_id || !payload.status) {
    return res.send("ok"); // nothing to do — don't trigger retries
  }
  deliver(payload);
  res.send("ok"); // 2xx stops CleanTrade retries
});

app.get("/healthz", (req, res) => {
  res.json({ ok: true });
});

const PORT = process.env.PORT || 8081;
if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`CleanTrade webhook receiver listening on :${PORT}`);
    console.log(`Webhook URL: http://<your-public-host>:${PORT}/hook`);
  });
}

module.exports = { app, createOrder, deliver };
