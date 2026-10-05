// Minimal PayPal Orders v2 client.
function base(env) {
  return env === 'live' ? 'https://api-m.paypal.com' : 'https://api-m.sandbox.paypal.com';
}

async function accessToken(s) {
  const auth = Buffer.from(`${s.paypal_client_id}:${s.paypal_secret}`).toString('base64');
  const r = await fetch(`${base(s.paypal_env)}/v1/oauth2/token`, {
    method: 'POST',
    headers: { Authorization: `Basic ${auth}`, 'Content-Type': 'application/x-www-form-urlencoded' },
    body: 'grant_type=client_credentials',
  });
  if (!r.ok) throw new Error(`PayPal auth failed (${r.status})`);
  return (await r.json()).access_token;
}

// Capture an approved order; if already captured, fetch it instead. Returns the order object.
export async function captureOrder(s, orderID) {
  const tok = await accessToken(s);
  const h = { Authorization: `Bearer ${tok}`, 'Content-Type': 'application/json' };
  const cap = await fetch(`${base(s.paypal_env)}/v2/checkout/orders/${orderID}/capture`, {
    method: 'POST', headers: { ...h, 'PayPal-Request-Id': orderID },
  });
  if (cap.ok) return cap.json();
  const get = await fetch(`${base(s.paypal_env)}/v2/checkout/orders/${orderID}`, { headers: h });
  if (!get.ok) throw new Error(`PayPal order lookup failed (${get.status})`);
  return get.json();
}

// Pull the bits we care about out of an order object.
export function summarize(order) {
  const unit = order.purchase_units?.[0];
  const capture = unit?.payments?.captures?.[0];
  return {
    paid: order.status === 'COMPLETED' && capture?.status === 'COMPLETED',
    captureId: capture?.id || null,
    amount: capture?.amount?.value,
    currency: capture?.amount?.currency_code,
    email: order.payer?.email_address || null,
    name: [order.payer?.name?.given_name, order.payer?.name?.surname].filter(Boolean).join(' ') || null,
  };
}

// Verify credentials from the admin settings page.
export async function testCredentials(s) {
  await accessToken(s);
  return true;
}
